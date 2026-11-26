"""
Terrain server: geomorphometry tools added on top of the upstream DORA tool library.

Four tools, no model weights, no new third-party dependencies beyond what DORA already
ships (numpy / rasterio / scikit-image / shapely):

- ``ras.terrain``    — slope, aspect, curvature, TRI, TPI and roughness in one pass
- ``ras.flow``       — depression filling (priority-flood), D8 flow direction, flow accumulation
- ``ras.catchment``  — watershed upstream of one or more pour points, as raster + polygon
- ``ras.contour``    — contour lines as GeoJSON

Conventions follow the common GIS implementations so results are comparable with GDAL
``gdaldem`` (Horn 3x3 for slope/aspect), Zevenbergen & Thorne (1987) for curvature,
Riley et al. (1999) for TRI, Weiss (2001) for TPI, and Barnes et al. (2014) for the
priority-flood depression filling.

Differences from ``ras.slope`` / ``ras.hillshade`` in ``analysis.py`` (kept unchanged for
compatibility): those use ``np.gradient`` and take ``transform.a`` as the cell size in
metres, which is wrong for a geographic CRS. ``ras.terrain`` converts degrees to metres
using the scene's mean latitude and reports the cell size it used.
"""
import heapq
import json
import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from fastmcp import FastMCP

from ._common import session_temp_dir

mcp = FastMCP()
TEMP_DIR = session_temp_dir()

# D8 neighbourhood, clockwise from east, with the ESRI flow-direction codes.
_D8 = [(0, 1, 1), (1, 1, 2), (1, 0, 4), (1, -1, 8),
       (0, -1, 16), (-1, -1, 32), (-1, 0, 64), (-1, 1, 128)]

ALL_ATTRIBUTES = ("slope", "aspect", "curvature", "tri", "tpi", "roughness")


def _error(tool: str, exc: Exception, **inputs: Any) -> str:
    return json.dumps({"tool": tool, "error": str(exc), "inputs": inputs}, ensure_ascii=False)


def _read_dem(dem_path: str) -> Tuple[np.ndarray, Optional[Any], Optional[Any], Optional[dict]]:
    """Read a single-band DEM, returning ``(array, transform, crs, profile)``."""
    import rasterio

    with rasterio.open(dem_path) as src:
        dem = src.read(1).astype(np.float64)
        nodata = src.nodata
        profile = src.profile.copy()
        transform, crs = src.transform, src.crs
    if nodata is not None:
        dem[dem == nodata] = np.nan
    return dem, transform, crs, profile


def _cell_size_m(transform, crs) -> Tuple[float, float, Optional[str]]:
    """Cell size in metres. A geographic CRS is converted with the scene's mean latitude."""
    xres, yres = abs(transform.a), abs(transform.e)
    if crs is not None and getattr(crs, "is_geographic", False):
        # Mean latitude of the raster, derived from the transform and the array shape.
        lat = transform.f
        mx = 111_320.0 * max(math.cos(math.radians(abs(lat))), 1e-6)
        return xres * mx, yres * 110_540.0, "geographic CRS: degrees converted to metres at the top latitude"
    return xres, yres, None


def _neighbours(dem: np.ndarray) -> List[np.ndarray]:
    """The eight 3x3 neighbours, edge-padded so shapes match ``dem``."""
    p = np.pad(dem, 1, mode="edge")
    h, w = dem.shape
    return [p[1 + dr:1 + dr + h, 1 + dc:1 + dc + w] for dr, dc in
            [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]]


def _write_raster(path: str, array: np.ndarray, profile: Optional[dict],
                  dtype: str = "float32") -> str:
    import rasterio

    if profile is None:                      # PNG input: no georeferencing to preserve
        np.save(path + ".npy", array)
        return path + ".npy"
    prof = profile.copy()
    prof.update(count=1, dtype=dtype, compress="deflate")
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(array.astype(dtype), 1)
    return path


def _stats(a: np.ndarray) -> Dict[str, float]:
    v = a[np.isfinite(a)]
    if v.size == 0:
        return {"min": 0.0, "max": 0.0, "mean": 0.0}
    return {"min": float(v.min()), "max": float(v.max()), "mean": float(v.mean())}


@mcp.tool(name="ras.terrain", description='''
Description:
Derive terrain attributes from a DEM in one pass: slope, aspect, curvature, TRI, TPI and roughness.
Uses the Horn 3x3 kernel (same as GDAL gdaldem) for slope and aspect, Zevenbergen-Thorne for
curvature, Riley et al. for TRI, Weiss for TPI and a 3x3 range for roughness.
A geographic CRS is handled by converting degrees to metres at the scene latitude, so the
result is not silently wrong on a lat/lon DEM.

Parameters:
- dem_path (str): Path to a single-band DEM (GeoTIFF); elevation in metres
- attributes (str, optional): Comma-separated subset of slope,aspect,curvature,tri,tpi,roughness
- units (str, optional): "degrees" (default) or "percent" for slope
- out_dir (str, optional): Directory for the outputs; defaults to the session temp directory

Returns:
- paths (dict): One GeoTIFF path per attribute
- stats (dict): min / max / mean per attribute
- cell_size_m (dict): Cell size actually used, and a note when the CRS was geographic
''')
def ras_terrain(dem_path: str, attributes: Optional[str] = None, units: str = "degrees",
                out_dir: Optional[str] = None) -> str:
    try:
        wanted = [a.strip().lower() for a in (attributes or ",".join(ALL_ATTRIBUTES)).split(",") if a.strip()]
        unknown = [a for a in wanted if a not in ALL_ATTRIBUTES]
        if unknown:
            raise ValueError(f"unknown attribute(s) {unknown}; choose from {list(ALL_ATTRIBUTES)}")
        if units not in ("degrees", "percent"):
            raise ValueError("units must be 'degrees' or 'percent'")

        dem, transform, crs, profile = _read_dem(dem_path)
        if transform is None:
            xres = yres = 1.0
            note = "no georeferencing: cell size assumed to be 1 m"
        else:
            xres, yres, note = _cell_size_m(transform, crs)

        # Horn 3x3: the same weights GDAL gdaldem uses by default.
        filled = np.where(np.isfinite(dem), dem, np.nanmean(dem))
        p = np.pad(filled, 1, mode="edge")
        h, w = dem.shape
        win = lambda dr, dc: p[1 + dr:1 + dr + h, 1 + dc:1 + dc + w]  # noqa: E731
        z1, z2, z3 = win(-1, -1), win(-1, 0), win(-1, 1)
        z4, z6 = win(0, -1), win(0, 1)
        z7, z8, z9 = win(1, -1), win(1, 0), win(1, 1)

        dzdx = ((z3 + 2 * z6 + z9) - (z1 + 2 * z4 + z7)) / (8 * xres)
        dzdy = ((z7 + 2 * z8 + z9) - (z1 + 2 * z2 + z3)) / (8 * yres)
        slope_rad = np.arctan(np.hypot(dzdx, dzdy))
        # `dzdy` here is (south - north); the downslope bearing clockwise from north is
        # atan2(-dzdx, dzdy), which gives 90 deg on a plane falling to the east.
        aspect = (np.degrees(np.arctan2(-dzdx, dzdy)) + 360.0) % 360.0

        out: Dict[str, np.ndarray] = {}
        if "slope" in wanted:
            out["slope"] = np.tan(slope_rad) * 100.0 if units == "percent" else np.degrees(slope_rad)
        if "aspect" in wanted:
            out["aspect"] = aspect
        if "curvature" in wanted:
            L2 = xres * yres
            D = ((z4 + z6) / 2.0 - filled) / (xres * xres)
            E = ((z2 + z8) / 2.0 - filled) / (yres * yres)
            out["curvature"] = -2.0 * (D + E) * 100.0     # per 100 m, as in ArcGIS
        if "tri" in wanted:
            nbrs = _neighbours(filled)
            out["tri"] = np.sqrt(sum((n - filled) ** 2 for n in nbrs))
        if "tpi" in wanted:
            nbrs = _neighbours(filled)
            out["tpi"] = filled - np.mean(nbrs, axis=0)
        if "roughness" in wanted:
            nbrs = _neighbours(filled)
            stack = np.stack(nbrs)
            out["roughness"] = stack.max(axis=0) - stack.min(axis=0)

        base = out_dir or str(TEMP_DIR)
        import os

        os.makedirs(base, exist_ok=True)
        paths, stats = {}, {}
        for name, arr in out.items():
            arr = np.where(np.isfinite(dem), arr, np.nan)
            paths[name] = _write_raster(os.path.join(base, f"terrain_{name}.tif"), arr, profile)
            stats[name] = _stats(arr)

        return json.dumps({
            "tool": "ras.terrain",
            "paths": paths,
            "stats": stats,
            "units": units if "slope" in out else None,
            "cell_size_m": {"x": float(xres), "y": float(yres), "note": note},
            "shape": [int(h), int(w)],
        }, ensure_ascii=False)
    except Exception as e:
        return _error("ras.terrain", e, dem_path=dem_path, attributes=attributes)


def _priority_flood(dem: np.ndarray, epsilon: float) -> Tuple[np.ndarray, int]:
    """Barnes et al. (2014) priority-flood with an epsilon gradient.

    Returns the filled DEM and the number of cells that were raised. Border cells seed the
    queue, so every interior depression is filled up to its lowest outlet.
    """
    h, w = dem.shape
    filled = dem.copy()
    closed = np.zeros((h, w), dtype=bool)
    heap: List[Tuple[float, int, int, int]] = []
    counter = 0

    def push(r: int, c: int) -> None:
        nonlocal counter
        heapq.heappush(heap, (filled[r, c], counter, r, c))
        counter += 1

    for r in range(h):
        for c in (0, w - 1):
            if not closed[r, c] and np.isfinite(filled[r, c]):
                push(r, c)
                closed[r, c] = True
    for c in range(w):
        for r in (0, h - 1):
            if not closed[r, c] and np.isfinite(filled[r, c]):
                push(r, c)
                closed[r, c] = True

    raised = 0
    while heap:
        z, _, r, c = heapq.heappop(heap)
        for dr, dc, _ in _D8:
            nr, nc = r + dr, c + dc
            if nr < 0 or nr >= h or nc < 0 or nc >= w or closed[nr, nc]:
                continue
            if not np.isfinite(filled[nr, nc]):
                closed[nr, nc] = True
                continue
            nz = max(filled[nr, nc], z + epsilon)
            if nz > filled[nr, nc]:
                raised += 1
            filled[nr, nc] = nz
            closed[nr, nc] = True
            push(nr, nc)
    return filled, raised


def _d8_direction(filled: np.ndarray, xres: float, yres: float) -> np.ndarray:
    """Steepest-descent D8, ESRI codes (1=E, 2=SE, 4=S ... 128=NE); 0 means no outlet."""
    h, w = filled.shape
    best = np.zeros((h, w), dtype=np.float32)
    best_slope = np.zeros((h, w), dtype=np.float64)
    for dr, dc, code in _D8:
        nbr = np.full((h, w), np.inf)
        rs = slice(max(0, dr), h + min(0, dr))
        rd = slice(max(0, -dr), h + min(0, -dr))
        cs = slice(max(0, dc), w + min(0, dc))
        cd = slice(max(0, -dc), w + min(0, -dc))
        nbr[rd, cd] = filled[rs, cs]
        dist = math.hypot(dr * yres, dc * xres)
        drop = (filled - nbr) / dist           # positive where the neighbour is lower
        better = (drop > best_slope) & np.isfinite(nbr)
        best_slope[better] = drop[better]
        best[better] = code
    return best


# Lookup tables from an ESRI direction code to the (row, col) step it encodes.
_LUT_DR = np.zeros(129, dtype=np.int64)
_LUT_DC = np.zeros(129, dtype=np.int64)
for _dr, _dc, _code in _D8:
    _LUT_DR[_code] = _dr
    _LUT_DC[_code] = _dc


def _downstream_index(direction: np.ndarray) -> np.ndarray:
    """Flat index of the cell each cell drains into, or -1 for an outlet / edge cell."""
    h, w = direction.shape
    code = direction.ravel().astype(np.int64)
    valid = (code > 0) & (code < 129)
    safe = np.where(valid, code, 0)
    idx = np.arange(h * w)
    nr = idx // w + _LUT_DR[safe]
    nc = idx % w + _LUT_DC[safe]
    ok = valid & (nr >= 0) & (nr < h) & (nc >= 0) & (nc < w)
    return np.where(ok, nr * w + nc, -1)


def _flow_grids(dem: np.ndarray, xres: float, yres: float, fill: bool = True,
                epsilon: float = 1e-4) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    """Fill, route and accumulate in one go.

    Returns ``(filled, direction, accumulation, order_desc, raised)`` where ``order_desc``
    sorts the cells from the highest filled elevation down. The epsilon gradient makes that
    order a valid topological order for D8, so accumulation is a single pass; reversing it
    gives the upstream→downstream order used by ``ras.catchment``.
    """
    raised = 0
    filled = dem
    if fill:
        filled, raised = _priority_flood(dem, epsilon)

    direction = _d8_direction(filled, xres, yres)
    target = _downstream_index(direction)

    h, w = filled.shape
    acc = np.ones(h * w, dtype=np.float64)
    order = np.argsort(filled, axis=None)[::-1]
    acc_dst = acc                               # same buffer, written in place
    for idx in order:
        nxt = target[idx]
        if nxt >= 0:
            acc_dst[nxt] += acc_dst[idx]
    return filled, direction, acc.reshape(h, w), order, raised


@mcp.tool(name="ras.flow", description='''
Description:
Hydrological terrain analysis: fill depressions, compute D8 flow direction and flow accumulation,
and optionally extract a river network above an accumulation threshold.
This is the physical starting point for catchment and flood-routing work, which the upstream
library does not cover.

Parameters:
- dem_path (str): Path to a single-band DEM (GeoTIFF); elevation in metres
- fill (bool, optional): Fill depressions before routing (default True)
- epsilon (float, optional): Elevation increment used to give flats a gradient (default 1e-4 m)
- river_threshold (int, optional): Extract cells whose accumulation reaches this value
- out_dir (str, optional): Directory for the outputs; defaults to the session temp directory

Returns:
- paths (dict): filled DEM, flow direction, flow accumulation, optional river raster
- stats (dict): max accumulation, number of outlets, filled cell count
- cell_size_m (dict): Cell size used (degrees are converted to metres)
''')
def ras_flow(dem_path: str, fill: bool = True, epsilon: float = 1e-4,
             river_threshold: Optional[int] = None, out_dir: Optional[str] = None) -> str:
    try:
        if epsilon <= 0:
            raise ValueError("epsilon must be positive")
        dem, transform, crs, profile = _read_dem(dem_path)
        if not np.isfinite(dem).all():
            dem = np.where(np.isfinite(dem), dem, np.nanmean(dem))
        xres, yres, note = (_cell_size_m(transform, crs) if transform is not None
                            else (1.0, 1.0, "no georeferencing: cell size assumed to be 1 m"))

        filled, direction, acc, _order, raised = _flow_grids(dem, xres, yres, fill, epsilon)
        h, w = filled.shape

        base = out_dir or str(TEMP_DIR)
        import os

        os.makedirs(base, exist_ok=True)
        paths = {}
        if fill:
            paths["filled"] = _write_raster(os.path.join(base, "flow_filled.tif"), filled, profile)
        paths["flow_direction"] = _write_raster(os.path.join(base, "flow_direction.tif"), direction, profile)
        paths["flow_accumulation"] = _write_raster(os.path.join(base, "flow_accumulation.tif"), acc, profile)

        river = None
        if river_threshold is not None:
            if river_threshold < 1:
                raise ValueError("river_threshold must be >= 1")
            river = (acc >= float(river_threshold)).astype(np.float32)
            paths["river"] = _write_raster(os.path.join(base, "flow_river.tif"), river, profile)

        return json.dumps({
            "tool": "ras.flow",
            "paths": paths,
            "stats": {
                "max_accumulation": float(acc.max()),
                "outlet_count": int((direction == 0).sum()),
                "filled_cells": int(raised),
                "river_cells": int(river.sum()) if river is not None else None,
            },
            "cell_size_m": {"x": float(xres), "y": float(yres), "note": note},
            "shape": [int(h), int(w)],
        }, ensure_ascii=False)
    except Exception as e:
        return _error("ras.flow", e, dem_path=dem_path, river_threshold=river_threshold)


def _parse_points(spec: str) -> List[Tuple[float, float]]:
    """Parse ``"x,y;x,y"`` (or space-separated) into a list of pairs."""
    pts: List[Tuple[float, float]] = []
    for chunk in spec.replace(";", " ").replace("|", " ").replace("\n", " ").split():
        parts = [p for p in chunk.split(",") if p.strip()]
        if len(parts) != 2:
            raise ValueError(f"cannot read point {chunk!r}; expected 'x,y' pairs separated by ';'")
        pts.append((float(parts[0]), float(parts[1])))
    if not pts:
        raise ValueError("pour_points is empty")
    return pts


def _side_counts(mask: np.ndarray) -> Dict[str, int]:
    """True cells on each edge; corners are counted once, so the four numbers add up."""
    return {"top": int(mask[0, :].sum()), "bottom": int(mask[-1, :].sum()),
            "left": int(mask[1:-1, 0].sum()), "right": int(mask[1:-1, -1].sum())}


@mcp.tool(name="ras.catchment", description='''
Description:
Delineate the catchment (watershed / contributing area) upstream of one or more pour points.
Reuses the same depression filling, D8 routing and flow accumulation as ras.flow, then walks
the flow graph backwards from each outlet. Each cell is assigned to the first outlet it reaches
on its way downstream, so several pour points split the tile into disjoint sub-catchments whose
areas add up; with a single outlet that is simply its watershed.

Pour points can be given in the DEM's own CRS ("same", the default), as WGS84 lon/lat
("wgs84", reprojected to the DEM CRS), or as 0-based pixel ("pixel", written as col,row).
Omitting pour_points uses the lowest cell on the DEM border, i.e. the outlet of the whole tile.

Parameters:
- dem_path (str): Path to a single-band DEM (GeoTIFF); elevation in metres
- pour_points (str, optional): "x,y;x,y" - ";", "|" or whitespace separated. Default: lowest border cell
- pour_crs (str, optional): "same" (default) | "wgs84" | "pixel"
- snap_radius_m (float, optional): Move each point to the highest-accumulation cell within this radius; 0 = exact cell
- min_area_cells (int, optional): Drop catchments smaller than this and report them (default 1)
- simplify_m (float, optional): Douglas-Peucker tolerance for the polygons (default 0 = keep all vertices)
- out_dir (str, optional): Output directory; defaults to the session temp directory
- out_geojson (str, optional): GeoJSON path for the polygons

Returns:
- outlets (list): per outlet - pixel, cells, area_km2, elevation range, border contact
- paths (dict): catchment label raster (1..n) and the GeoJSON polygons
- truncation (dict): how much of the catchment touches the tile edge, and what that implies
- warnings (list): pour points that control almost no area, etc.
''')
def ras_catchment(dem_path: str, pour_points: Optional[str] = None, pour_crs: str = "same",
                  snap_radius_m: float = 0.0, min_area_cells: int = 1,
                  simplify_m: float = 0.0, out_dir: Optional[str] = None,
                  out_geojson: Optional[str] = None) -> str:
    try:
        import os

        if pour_crs not in ("same", "wgs84", "pixel"):
            raise ValueError("pour_crs must be 'same', 'wgs84' or 'pixel'")
        if snap_radius_m < 0:
            raise ValueError("snap_radius_m must be >= 0")
        if min_area_cells < 1:
            raise ValueError("min_area_cells must be >= 1")

        dem, transform, crs, profile = _read_dem(dem_path)
        if not np.isfinite(dem).all():
            dem = np.where(np.isfinite(dem), dem, np.nanmean(dem))
        if transform is None:
            xres = yres = 1.0
            note = "no georeferencing: cell size assumed to be 1 m, coordinates read as pixels"
        else:
            xres, yres, note = _cell_size_m(transform, crs)

        filled, direction, acc, order, raised = _flow_grids(dem, xres, yres, True, 1e-4)
        h, w = filled.shape
        n_cells = h * w
        target = _downstream_index(direction)

        # ---- pour points -> pixel ----
        auto_selected = pour_points is None
        warnings: List[str] = []
        if auto_selected:
            edge = np.zeros((h, w), dtype=bool)
            edge[0, :] = edge[-1, :] = edge[:, 0] = edge[:, -1] = True
            flat = int(np.argmin(np.where(edge, filled, np.inf)))
            raw_pts = [(float(int(flat % w)), float(int(flat // w)))]
            pour_crs = "pixel"
        else:
            raw_pts = _parse_points(pour_points)

        transformer = None
        if pour_crs == "wgs84":
            if crs is None or transform is None:
                raise ValueError("pour_crs='wgs84' needs a georeferenced DEM")
            from pyproj import Transformer

            transformer = Transformer.from_crs("EPSG:4326", crs, always_xy=True)

        pixel_pts: List[Tuple[int, int]] = []
        for k, (a, b) in enumerate(raw_pts):
            if pour_crs == "pixel":
                col_f, row_f = a, b
            else:
                x, y = a, b
                if transformer is not None:
                    x, y = transformer.transform(x, y)
                col_f, row_f = (~transform * (x, y))
            # floor, not round: the fractional part is the position inside the cell, so
            # round() would push a point sitting exactly on a cell edge into the next cell.
            row_i, col_i = int(math.floor(row_f + 1e-9)), int(math.floor(col_f + 1e-9))
            if not (0 <= row_i < h and 0 <= col_i < w):
                raise ValueError(
                    f"pour point {k + 1} ({a}, {b}) falls outside the DEM; "
                    f"the raster spans {w} columns x {h} rows")
            pixel_pts.append((row_i, col_i))

        # ---- optional snapping to the strongest channel nearby ----
        rx = int(math.ceil(snap_radius_m / xres)) if snap_radius_m > 0 else 0
        ry = int(math.ceil(snap_radius_m / yres)) if snap_radius_m > 0 else 0
        snapped_info: List[Dict[str, Any]] = []
        for k, (r0, c0) in enumerate(pixel_pts):
            chosen, dist = (r0, c0), 0.0
            if snap_radius_m > 0:
                r1, r2 = max(0, r0 - ry), min(h, r0 + ry + 1)
                c1, c2 = max(0, c0 - rx), min(w, c0 + rx + 1)
                win = acc[r1:r2, c1:c2]
                d = np.hypot((np.arange(r1, r2)[:, None] - r0) * yres,
                             (np.arange(c1, c2)[None, :] - c0) * xres)
                score = np.where(d <= snap_radius_m, win, -1.0)
                j = int(np.argmax(score))
                wr, wc = divmod(j, win.shape[1])
                if score[wr, wc] > 0:
                    chosen = (r1 + wr, c1 + wc)
                    dist = float(d[wr, wc])
            pixel_pts[k] = chosen
            snapped_info.append({"snapped": chosen != (r0, c0),
                                 "snap_distance_m": round(dist, 2)})

        # Two pour points that land on the same cell (or snapped onto it) would fight over
        # the same label; keep the first and say so.
        seen_at: Dict[Tuple[int, int], int] = {}
        kept_pts: List[Tuple[int, int]] = []
        kept_snaps: List[Dict[str, Any]] = []
        kept_raw: List[Tuple[float, float]] = []
        for k, px in enumerate(pixel_pts):
            if px in seen_at:
                warnings.append(
                    f"pour point {k + 1} landed on the same cell as pour point "
                    f"{seen_at[px] + 1} (row {px[0]}, col {px[1]}); kept the first one")
                continue
            seen_at[px] = k
            kept_pts.append(px)
            kept_snaps.append(snapped_info[k])
            kept_raw.append(raw_pts[k])
        pixel_pts, snapped_info, raw_pts = kept_pts, kept_snaps, kept_raw

        # ---- label cells with the outlet they drain to ----
        # Walking the cells from low to high means every cell meets its downstream
        # neighbour already labelled, so one pass assigns the whole network.
        owner = [0] * n_cells
        outlet_ids = list(range(1, len(pixel_pts) + 1))
        for oid, (r, c) in zip(outlet_ids, pixel_pts):
            owner[r * w + c] = oid
        for idx in order[::-1]:
            if owner[idx]:
                continue
            nxt = target[idx]
            if nxt >= 0 and owner[nxt]:
                owner[idx] = owner[nxt]
        lab = np.fromiter(owner, dtype=np.int16 if len(pixel_pts) < 32767 else np.int32,
                          count=n_cells).reshape(h, w)

        border = np.zeros((h, w), dtype=bool)
        border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True

        outlets: List[Dict[str, Any]] = []
        keep = []
        shown_crs = "pixel" if (auto_selected and transform is None) else (
            "same" if auto_selected else pour_crs)
        for oid, (r, c) in zip(outlet_ids, pixel_pts):
            sel = lab == oid
            cells = int(sel.sum())
            if cells < min_area_cells:
                warnings.append(
                    f"pour point at row {r}, col {c} controls {cells} cell(s) and was dropped; "
                    f"it is probably not on a flow path - try snap_radius_m=300")
                continue
            keep.append(oid)
            vals = filled[sel]
            if auto_selected:
                if transform is not None:
                    x, y = transform * (c + 0.5, r + 0.5)
                    pp = [round(float(x), 3), round(float(y), 3)]
                else:
                    pp = [c, r]
            else:
                pp = raw_pts[oid - 1]
            outlets.append({
                "id": oid,
                "pour_point": [round(float(v), 6) if isinstance(v, float) else v for v in pp],
                "pour_crs": shown_crs,
                "pixel": [r, c],
                "snapped": snapped_info[oid - 1]["snapped"],
                "snap_distance_m": snapped_info[oid - 1]["snap_distance_m"],
                "cells": cells,
                "area_km2": round(cells * xres * yres / 1e6, 4),
                "share_of_tile": round(cells / n_cells, 4),
                "elevation_range_m": [round(float(vals.min()), 1), round(float(vals.max()), 1)],
                "outlet_accumulation": round(float(acc[r, c]), 1),
                "touches_border": bool((sel & border).any()),
                "border_cells": int((sel & border).sum()),
                "border_by_side": _side_counts(sel & border),
            })

        if not keep:
            raise ValueError("no catchment survived min_area_cells; see warnings")

        # Drop the labels of discarded outlets so the raster only holds kept ids.
        if len(keep) != len(outlet_ids):
            remap = np.zeros(int(lab.max()) + 1, dtype=lab.dtype)
            for new_id, old_id in enumerate(keep, start=1):
                remap[old_id] = new_id
            lab = remap[lab]
            for i, o in enumerate(outlets, start=1):
                o["id"] = i

        # ---- border / truncation accounting ----
        union = lab > 0
        on_border = union & border
        by_side = _side_counts(on_border)
        border_acc = float(acc[on_border].max()) if on_border.any() else 0.0
        # Cells where water leaves the tile (or the dataset) entirely.
        exits = int(((direction == 0) & union & border).sum())
        outlet_on_border = any(border[r, c] for r, c in pixel_pts)

        if not on_border.any():
            border_note = ("Nothing of the catchment touches the tile edge, so no upstream area is "
                    "missing as far as this DEM can tell: the watershed closes inside the tile.")
        else:
            sides = ", ".join(f"{k} {v}" for k, v in by_side.items() if v)
            border_note = (f"{int(on_border.sum())} catchment cell(s) lie on the tile edge ({sides}). "
                    "The DEM ends there, so whatever drains in from beyond it is invisible "
                    "and the reported area is a lower bound. "
                    + ("The outlet itself is on the edge, so the downstream part is outside too. "
                       if outlet_on_border else
                       "No outlet sits on the edge, so what is cut off is upstream. ")
                    + (f"The largest accumulation on the edge is {border_acc:.0f} cells - a large "
                       "value means a channel is severed by the boundary and closing it with the "
                       "neighbouring tile matters."
                       if border_acc > 1 else
                       "Every edge cell carries a single cell of runoff, which is what a watershed "
                       "divide touching the corner of a tile looks like: probably nothing lost."))
        truncation = {
            "touches_border": bool(on_border.any()),
            "border_cells": int(on_border.sum()),
            "by_side": by_side,
            "outlet_on_border": bool(outlet_on_border),
            "exits_on_border": exits,
            "max_accumulation_on_border": round(border_acc, 1),
            "may_be_incomplete": bool(on_border.any()),
            "note": border_note,
            "how_to_close": ("Mosaic the neighbouring tiles, or buffer the DEM by a few km and "
                             "re-run, if the boundary cut matters for the question."),
        }

        # ---- write raster ----
        base = out_dir or str(TEMP_DIR)
        os.makedirs(base, exist_ok=True)
        paths: Dict[str, Any] = {
            "catchment": _write_raster(os.path.join(base, "catchment.tif"), lab, profile,
                                       dtype="int16" if lab.dtype == np.int16 else "int32"),
        }

        # ---- polygons ----
        geojson_path = None
        if transform is not None and profile is not None:
            try:
                from rasterio import features
                from shapely.geometry import mapping, shape
                from shapely.ops import unary_union

                groups: Dict[int, list] = {}
                for geom, val in features.shapes(lab, mask=union, transform=transform,
                                                 connectivity=8):
                    groups.setdefault(int(val), []).append(shape(geom))
                feats = []
                for o in outlets:
                    polys = groups.get(o["id"], [])
                    if not polys:
                        continue
                    merged = unary_union(polys)
                    if simplify_m > 0:
                        merged = merged.simplify(simplify_m, preserve_topology=True)
                    feats.append({"type": "Feature",
                                  "properties": {"id": o["id"], "area_km2": o["area_km2"],
                                                 "cells": o["cells"]},
                                  "geometry": mapping(merged)})
                dest = out_geojson or os.path.join(base, "catchment.geojson")
                os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
                crs_name = crs.to_string() if crs is not None else None
                with open(dest, "w", encoding="utf-8") as f:
                    json.dump({"type": "FeatureCollection", "name": "catchments",
                               "crs": ({"type": "name", "properties": {"name": crs_name}}
                                       if crs_name else None),
                               "features": feats}, f, ensure_ascii=False)
                geojson_path = dest
            except ImportError as exc:               # shapely missing: raster is still useful
                warnings.append(f"polygon output skipped ({exc})")
        elif transform is None:
            warnings.append("no georeferencing: polygons skipped, use the label raster")

        if geojson_path:
            paths["catchment_geojson"] = geojson_path

        for o in outlets:
            if o["cells"] <= 1:
                warnings.append(
                    f"outlet {o['id']} controls a single cell: no mapped upstream, so it is "
                    f"either on a ridge or off the D8 flow path. Try snap_radius_m=300")

        return json.dumps({
            "tool": "ras.catchment",
            "outlets": outlets,
            "paths": paths,
            "truncation": truncation,
            "warnings": warnings,
            "fill": {"enabled": True, "filled_cells": int(raised)},
            "cell_size_m": {"x": float(xres), "y": float(yres), "note": note},
            "shape": [int(h), int(w)],
            "summary": f"{len(keep)} catchment(s) over {n_cells} cells",
        }, ensure_ascii=False)
    except Exception as e:
        return _error("ras.catchment", e, dem_path=dem_path, pour_points=pour_points)


@mcp.tool(name="ras.contour", description='''
Description:
Extract contour lines (isolines) from a DEM at a fixed interval and write them as GeoJSON
LineStrings with the elevation as an attribute. Useful for cartography and for slope-class
base maps.

Parameters:
- dem_path (str): Path to a single-band DEM (GeoTIFF)
- interval (float): Vertical interval between contour lines, in DEM units
- base (float, optional): First contour level; defaults to the next multiple of interval
- min_length (float, optional): Drop lines shorter than this many metres (default 0)
- out_path (str, optional): GeoJSON output path

Returns:
- out_path (str): GeoJSON with one feature per contour line
- n_lines (int): Number of lines written
- levels (list[float]): Contour levels present in the output
- total_length_m (float): Summed length of all lines
''')
def ras_contour(dem_path: str, interval: float, base: Optional[float] = None,
                min_length: float = 0.0, out_path: Optional[str] = None) -> str:
    try:
        if interval <= 0:
            raise ValueError("interval must be positive")
        from skimage import measure

        dem, transform, crs, profile = _read_dem(dem_path)
        vmin, vmax = float(np.nanmin(dem)), float(np.nanmax(dem))
        start = base if base is not None else math.ceil(vmin / interval) * interval
        levels = []
        lv = start
        while lv <= vmax:
            if lv > vmin:
                levels.append(round(float(lv), 6))
            lv += interval
        if not levels:
            raise ValueError(f"no contour level between {vmin:.3f} and {vmax:.3f} with interval {interval}")

        work = np.where(np.isfinite(dem), dem, vmin - interval)
        xres, yres, _ = (_cell_size_m(transform, crs) if transform is not None else (1.0, 1.0, None))
        features, total_length = [], 0.0
        for level in levels:
            for path in measure.find_contours(work, level, fully_connected="low", positive_orientation="low"):
                if path.shape[0] < 2:
                    continue
                rows, cols = path[:, 0], path[:, 1]
                if transform is not None:
                    xs = transform.c + transform.a * cols + transform.b * rows
                    ys = transform.f + transform.d * cols + transform.e * rows
                else:
                    xs, ys = cols, -rows
                seg = np.hypot(np.diff(cols) * xres, np.diff(rows) * yres)
                length = float(seg.sum())
                if length < min_length:
                    continue
                total_length += length
                features.append({
                    "type": "Feature",
                    "properties": {"elevation": level, "length_m": round(length, 2)},
                    "geometry": {"type": "LineString",
                                 "coordinates": [[round(float(x), 6), round(float(y), 6)]
                                                 for x, y in zip(xs, ys)]},
                })

        import os

        dest = out_path or os.path.join(str(TEMP_DIR), "contour.geojson")
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        crs_name = crs.to_string() if crs is not None else None
        payload = {"type": "FeatureCollection",
                   "name": "contours",
                   "crs": {"type": "name", "properties": {"name": crs_name}} if crs_name else None,
                   "features": features}
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)

        return json.dumps({
            "tool": "ras.contour",
            "out_path": dest,
            "n_lines": len(features),
            "levels": levels,
            "total_length_m": round(total_length, 1),
            "interval": interval,
            "elevation_range": [vmin, vmax],
        }, ensure_ascii=False)
    except Exception as e:
        return _error("ras.contour", e, dem_path=dem_path, interval=interval)


# ============== MCP entry point ==============

if __name__ == "__main__":
    mcp.run(show_banner=False)
