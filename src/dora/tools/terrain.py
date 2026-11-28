"""
Terrain server: geomorphometry tools added on top of the upstream DORA tool library.

Seven tools, no model weights, no new third-party dependencies beyond what DORA already
ships (numpy / rasterio / scikit-image / shapely):

- ``ras.terrain``      — slope, aspect, curvature, TRI, TPI and roughness in one pass
- ``ras.geomorphons``  — the 10 common landform units from line-of-sight patterns
- ``ras.flow``         — depression filling (priority-flood), D8 flow direction, flow accumulation
- ``ras.catchment``    — watershed upstream of one or more pour points, as raster + polygon
- ``ras.river_network``— drainage network as ordered reaches (Strahler) with topology
- ``ras.hand``        — height above nearest drainage, and inundation for a given water stage
- ``ras.contour``      — contour lines as GeoJSON

Conventions follow the common GIS implementations so results are comparable with GDAL
``gdaldem`` (Horn 3x3 for slope/aspect), Zevenbergen & Thorne (1987) for curvature,
Riley et al. (1999) for TRI, Weiss (2001) for TPI, Barnes et al. (2014) for the
priority-flood depression filling, and Jasiewicz & Stepinski (2013) for geomorphons.

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


# Geomorphon directions, clockwise from north: (drow, dcol, is_diagonal).
_GEOM_DIRS = [(-1, 0, False), (-1, 1, True), (0, 1, False), (1, 1, True),
              (1, 0, False), (1, -1, True), (0, -1, False), (-1, -1, True)]

GEOM_CLASSES = ("flat", "peak", "ridge", "shoulder", "spur",
                "slope", "hollow", "footslope", "valley", "pit")


def _shift(a: np.ndarray, dr: int, dc: int, fill: float) -> np.ndarray:
    """Translate ``a`` by (dr, dc), filling the vacated border instead of wrapping."""
    h, w = a.shape
    out = np.full((h, w), fill, dtype=a.dtype)
    rs, rd = slice(max(0, dr), h + min(0, dr)), slice(max(0, -dr), h + min(0, -dr))
    cs, cd = slice(max(0, dc), w + min(0, dc)), slice(max(0, -dc), w + min(0, -dc))
    out[rd, cd] = a[rs, cs]
    return out


def _ternary_pattern(dem: np.ndarray, xres: float, yres: float, search: int,
                     skip: int, flat_rad: float) -> np.ndarray:
    """8 layers of +1 / 0 / -1, one per compass direction, clockwise from north.

    Follows the dual line-of-sight rule of Jasiewicz & Stepinski (2013): along each ray take
    the steepest upward sight line (zenith) and the steepest downward one (nadir); the
    direction is +1 when the zenith clears the nadir by more than the flatness threshold,
    -1 when the nadir wins by that much, and 0 in between.
    """
    h, w = dem.shape
    tern = np.zeros((8, h, w), dtype=np.int8)
    # The radius is a real distance, as in r.geomorphon: a diagonal ray covers sqrt(2) more
    # ground per step, so it reaches the radius after fewer steps than a straight one.
    search_m = search * yres
    for k, (dr, dc, _diag) in enumerate(_GEOM_DIRS):
        up = np.full((h, w), -np.inf)
        down = np.full((h, w), np.inf)
        step_m = math.hypot(dr * yres, dc * xres)
        for n in range(skip + 1, search + 1):
            dist = n * step_m
            if dist >= search_m:
                break
            nb = _shift(dem, dr * n, dc * n, np.nan)
            tan = (nb - dem) / dist
            up = np.fmax(up, tan)
            down = np.fmin(down, tan)
        # Same decision as the anglev1 mode of r.geomorphon: each line of sight is tested
        # against the threshold on its own, and when both clear it the steeper one wins.
        zen = np.arctan(up)
        nad = np.arctan(-down)
        tern[k] = np.where((zen > flat_rad) & (nad > flat_rad), np.where(zen > nad, 1, -1),
                           np.where(zen > flat_rad, 1,
                                    np.where(nad > flat_rad, -1, 0)))
    return tern


# The classification table published with r.geomorphon (legend.png in the module): rows are
# the number of rays looking down (-), columns the number looking up (+). Only the upper
# triangle is defined, since the two counts can never sum past 8. Classes:
# 1 flat, 2 peak, 3 ridge, 4 shoulder, 5 spur, 6 slope, 7 hollow, 8 footslope, 9 valley, 10 pit.
_GEOM_TABLE = (
    (1, 1, 1, 8, 8, 9, 9, 9, 10),      # 0 rays down
    (1, 1, 8, 8, 8, 9, 9, 9),          # 1
    (1, 4, 6, 6, 7, 7, 9),             # 2
    (4, 4, 6, 6, 6, 7),                # 3
    (4, 4, 5, 6, 6),                   # 4
    (3, 3, 5, 5),                      # 5
    (3, 3, 3),                         # 6
    (3, 3),                            # 7
    (2,),                              # 8
)


def _classify_geomorphons(n_plus: np.ndarray, n_minus: np.ndarray) -> np.ndarray:
    """Look up the landform code from the counts of rising and falling rays."""
    mat = np.zeros((9, 9), dtype=np.uint8)
    for m, row in enumerate(_GEOM_TABLE):
        mat[m, :len(row)] = row
    return mat[n_minus, n_plus]


@mcp.tool(name="ras.geomorphons", description='''
Description:
Classify every DEM cell into one of the ten common landform units - flat, peak, ridge,
shoulder, spur, slope, hollow, footslope, valley, pit - using the geomorphon method of
Jasiewicz & Stepinski (2013). Terrain is read as a pattern, not as derivatives: from each cell
eight rays are cast and each records whether the visible horizon rises above or falls below
it; that 8-symbol pattern names the landform. The result is categorical and scale-explicit:
search_distance sets the size of the landform, so a ridge at 100 m is a slope at 2 km.

Parameters:
- dem_path (str): Path to a single-band DEM (GeoTIFF); elevation in metres
- search_distance (int, optional): Look-out radius in cells (default 10); sets the landform size
- flatness_deg (float, optional): Angle in degrees below which a ray counts as level (default 1)
- skip_distance (int, optional): Ignore this many cells next to the centre, to suppress noise (default 0)
- return_pattern (bool, optional): Also write the ternary pattern code per cell, for diagnosis
- out_dir (str, optional): Directory for the outputs; defaults to the session temp directory

Returns:
- path (str): Categorical raster, values 1-10
- classes (dict): code -> name
- share (dict): fraction of valid cells in each class
- pattern_path (str): present only when return_pattern is true
- cell_size_m (dict): Cell size used (degrees are converted to metres)
''')
def ras_geomorphons(dem_path: str, search_distance: int = 10, flatness_deg: float = 1.0,
                    skip_distance: int = 0, return_pattern: bool = False,
                    out_dir: Optional[str] = None) -> str:
    try:
        import os

        if search_distance < 1:
            raise ValueError("search_distance must be >= 1")
        if skip_distance < 0 or skip_distance >= search_distance:
            raise ValueError("skip_distance must be >= 0 and smaller than search_distance")
        if flatness_deg <= 0:
            raise ValueError("flatness_deg must be positive")

        dem, transform, crs, profile = _read_dem(dem_path)
        xres, yres, note = (_cell_size_m(transform, crs) if transform is not None
                            else (1.0, 1.0, "no georeferencing: cell size assumed to be 1 m"))
        h, w = dem.shape

        valid = np.isfinite(dem)
        work = np.where(valid, dem, np.nan)

        tern = _ternary_pattern(work, xres, yres, search_distance, skip_distance,
                                math.radians(flatness_deg))
        n_plus = (tern == 1).sum(axis=0).astype(np.int16)
        n_minus = (tern == -1).sum(axis=0).astype(np.int16)
        cls = _classify_geomorphons(n_plus, n_minus)
        cls[~valid] = 0

        base = out_dir or str(TEMP_DIR)
        os.makedirs(base, exist_ok=True)
        paths: Dict[str, str] = {
            "geomorphons": _write_raster(os.path.join(base, "geomorphons.tif"), cls, profile,
                                         dtype="uint8"),
        }

        counts = {name: int((cls == code).sum())
                  for code, name in enumerate(GEOM_CLASSES, start=1)}
        total = int(valid.sum()) or 1

        if return_pattern:
            # Ternary code, base 3, direction 0 as the most significant digit.
            code = np.zeros((h, w), dtype=np.int32)
            for k in range(8):
                code = code * 3 + (tern[k].astype(np.int32) + 1)
            code[~valid] = -1
            paths["pattern"] = _write_raster(os.path.join(base, "geomorphon_pattern.tif"),
                                             code, profile, dtype="int32")

        return json.dumps({
            "tool": "ras.geomorphons",
            "path": paths["geomorphons"],
            "paths": paths,
            "classes": {str(i): n for i, n in enumerate(GEOM_CLASSES, start=1)},
            "share": {n: round(counts[n] / total, 4) for n in GEOM_CLASSES},
            "counts": counts,
            "params": {"search_distance": search_distance, "flatness_deg": flatness_deg,
                       "skip_distance": skip_distance},
            "cell_size_m": {"x": float(xres), "y": float(yres), "note": note},
            "shape": [int(h), int(w)],
        }, ensure_ascii=False)
    except Exception as e:
        return _error("ras.geomorphons", e, dem_path=dem_path,
                      search_distance=search_distance, flatness_deg=flatness_deg)


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


def _seg_length_m(coords: np.ndarray, transform, xres: float, yres: float) -> float:
    """Length of a polyline in metres.

    The coordinates are in the layer CRS, which for a geographic DEM means degrees, so the
    differences have to go back to pixel offsets first and then through the cell size that
    :func:`_cell_size_m` converted to metres.
    """
    if coords.shape[0] < 2:
        return 0.0
    if transform is None:
        dx = np.diff(coords[:, 0]) * xres
        dy = np.diff(coords[:, 1]) * yres
    else:
        a, b, c, d, e, f = (transform.a, transform.b, transform.c,
                            transform.d, transform.e, transform.f)
        det = a * e - b * d
        x, y = coords[:, 0] - c, coords[:, 1] - f
        cols = (e * x - b * y) / det
        rows = (-d * x + a * y) / det
        dx = np.diff(cols) * xres
        dy = np.diff(rows) * yres
    return float(np.hypot(dx, dy).sum())


def _cell_xy(transform, rows: np.ndarray, cols: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Cell-centre coordinates, honouring rotation terms; pixel space if unreferenced."""
    if transform is None:
        return cols.astype(np.float64), -rows.astype(np.float64)
    xs = transform.c + transform.a * cols + transform.b * rows
    ys = transform.f + transform.d * cols + transform.e * rows
    return xs.astype(np.float64), ys.astype(np.float64)


@mcp.tool(name="ras.river_network", description='''
Description:
Vectorise the D8 drainage network into reaches and order them with the Strahler scheme.
A reach is the chain of cells between two junctions (or between a source and the first
junction); its order is 1 at a source and, at a confluence, the maximum of the incoming
orders - raised by one only when every incoming reach shares that order. The result is the
unit flood routing and water-quality work is built on: each reach carries its order, length,
drop, slope and upstream area, plus a link to the reach below it.

Parameters:
- dem_path (str): Path to a single-band DEM (GeoTIFF); elevation in metres
- min_area_km2 (float, optional): Keep cells draining at least this area (default 1.0 km2)
- river_threshold (int, optional): Threshold in cells, overrides min_area_km2
- fill (bool, optional): Fill depressions before routing (default True)
- simplify_m (float, optional): Douglas-Peucker tolerance for the output lines (default 0)
- out_dir (str, optional): Directory for the outputs; defaults to the session temp directory

Returns:
- paths (dict): reaches (GeoJSON), nodes (GeoJSON), Strahler-order raster
- stats (dict): reach/junction/outlet counts, maximum order, total length
- by_order (dict): reach count and length per Strahler order
''')
def ras_river_network(dem_path: str, min_area_km2: float = 1.0,
                      river_threshold: Optional[int] = None, fill: bool = True,
                      simplify_m: float = 0.0, out_dir: Optional[str] = None) -> str:
    try:
        if river_threshold is not None and river_threshold < 2:
            raise ValueError("river_threshold must be >= 2 cells")
        if river_threshold is None and min_area_km2 <= 0:
            raise ValueError("min_area_km2 must be positive")

        dem, transform, crs, profile = _read_dem(dem_path)
        if not np.isfinite(dem).all():
            dem = np.where(np.isfinite(dem), dem, np.nanmean(dem))
        xres, yres, note = (_cell_size_m(transform, crs) if transform is not None
                            else (1.0, 1.0, "no georeferencing: cell size assumed to be 1 m"))
        cell_area = float(xres * yres)

        if river_threshold is not None:
            thresh, thresh_by = int(river_threshold), "river_threshold"
        else:
            thresh = max(2, int(round(min_area_km2 * 1e6 / cell_area)))
            thresh_by = "min_area_km2"

        filled, direction, acc, order, _raised = _flow_grids(dem, xres, yres, fill, 1e-4)
        h, w = filled.shape
        n = h * w
        target = _downstream_index(direction)
        acc_f = acc.ravel()
        elev_f = filled.ravel()
        river = acc_f >= thresh

        cells = np.flatnonzero(river)
        if cells.size < 3:
            raise ValueError(
                f"only {cells.size} cell(s) exceed the threshold ({thresh} cells); "
                f"lower min_area_km2 or river_threshold")

        # In-degree restricted to river cells: a junction is a cell with two or more
        # inflowing river cells. Accumulation is monotone downstream, so every river cell
        # drains into another river cell and the mask has no holes.
        src = cells[target[cells] >= 0]
        inflow = np.bincount(target[src], minlength=n).astype(np.int64)
        by_target = np.argsort(target[src], kind="stable")
        tgt_sorted = target[src][by_target]
        src_sorted = src[by_target]
        starts = np.zeros(n + 1, dtype=np.int64)
        np.cumsum(inflow, out=starts[1:])

        # Walk every cell once, from the highest filled elevation down, and give it the reach
        # of the cell above it unless it starts a reach itself (a source or a junction).
        pos = np.empty(n, dtype=np.int64)
        pos[order] = np.arange(n)
        reach = np.full(n, -1, dtype=np.int64)
        heads = np.flatnonzero(river & (inflow != 1))
        reach[heads] = heads
        # Every river cell records who drains into it. The cell above may itself be a reach
        # head (a source or a junction), so this must cover all cells, not only the ones with
        # a single inflow - otherwise the propagation below reads a -1 sentinel.
        up_of = np.full(n, -1, dtype=np.int64)
        up_of[target[src]] = src
        for idx in order[river[order]]:
            if reach[idx] < 0:
                reach[idx] = reach[up_of[idx]]

        # Group cells by reach, keeping each reach's own cells in upstream→downstream order.
        sel = cells[np.lexsort((pos[cells], reach[cells]))]
        rid = reach[sel]
        bounds = np.flatnonzero(np.r_[True, rid[1:] != rid[:-1]])
        r_head = rid[bounds]
        r_end = sel[np.r_[bounds[1:] - 1, sel.size - 1]]
        r_num = np.arange(r_head.size)
        r_slot = np.full(n, -1, dtype=np.int64)
        r_slot[r_head] = r_num
        down_cell = target[r_end]
        r_down = np.where(down_cell >= 0, r_slot[np.maximum(down_cell, 0)], -1)

        # Strahler and Shreve in topological order. A reach's head always sits higher than
        # any reach flowing into it, so sorting heads by elevation order is enough.
        strahler = np.zeros(r_head.size, dtype=np.int32)
        shreve = np.zeros(r_head.size, dtype=np.int64)
        for slot in r_num[np.argsort(pos[r_head])]:
            head = r_head[slot]
            ups = r_slot[reach[src_sorted[starts[head]:starts[head + 1]]]]
            if ups.size == 0:
                strahler[slot], shreve[slot] = 1, 1
            else:
                top = int(strahler[ups].max())
                strahler[slot] = top + 1 if (strahler[ups] == top).all() else top
                shreve[slot] = int(shreve[ups].sum())

        # Strahler order as a raster, one value per river cell (0 elsewhere).
        r_slot_of_group = r_slot[r_head]
        order_raster = np.zeros(n, dtype=np.float32)
        order_raster[sel] = np.repeat(strahler[r_slot_of_group],
                                      np.diff(np.r_[bounds, sel.size])).astype(np.float32)

        from shapely.geometry import LineString

        feats, node_feats = [], []
        by_order: Dict[int, Dict[str, float]] = {}
        total_length = 0.0
        for slot in range(r_head.size):
            b0 = bounds[slot]
            b1 = bounds[slot + 1] if slot + 1 < bounds.size else sel.size
            path = sel[b0:b1]
            rows, cols = path // w, path % w
            xs, ys = _cell_xy(transform, rows, cols)
            if path.size == 1:
                # Two junctions can sit next to each other, which leaves a one-cell reach.
                # Shapely needs two points, so stretch the line to the cell below (or to a
                # half-cell stub at a real outlet) instead of dropping the link.
                nxt = down_cell[slot]
                if nxt >= 0:
                    qr, qc = divmod(int(nxt), w)
                else:
                    qr, qc = int(rows[0]), int(cols[0]) + 1
                qx, qy = _cell_xy(transform, np.array([qr]), np.array([qc]))
                xs, ys = np.r_[xs, qx], np.r_[ys, qy]
            geom = LineString(np.column_stack([xs, ys]))
            if simplify_m > 0 and b1 - b0 > 3:
                geom = geom.simplify(simplify_m, preserve_topology=False)
                coords = np.asarray(geom.coords)
            else:
                coords = np.column_stack([xs, ys])
            length = _seg_length_m(coords, transform, xres, yres)
            drop = float(elev_f[r_head[slot]] - elev_f[r_end[slot]])
            # Straight-line distance between the ends, in the same metre grid.
            dr = float(rows[-1] - rows[0])
            dc = float(cols[-1] - cols[0])
            straight = math.hypot(dc * xres, dr * yres)
            area = float(acc_f[r_end[slot]] * cell_area / 1e6)
            k = int(strahler[slot])
            total_length += length
            bucket = by_order.setdefault(k, {"reaches": 0, "length_km": 0.0})
            bucket["reaches"] += 1
            bucket["length_km"] += length / 1000.0

            feats.append({
                "type": "Feature",
                "properties": {
                    "reach_id": slot + 1,
                    "strahler": k,
                    "magnitude": int(shreve[slot]),
                    "from_type": "source" if inflow[r_head[slot]] == 0 else "junction",
                    "to_type": "outlet" if r_down[slot] < 0 else "junction",
                    "downstream_reach": int(r_down[slot] + 1) if r_down[slot] >= 0 else None,
                    "length_m": round(length, 1),
                    "drop_m": round(drop, 2),
                    "mean_slope_deg": round(math.degrees(math.atan2(drop, length)), 3)
                                      if length > 0 else 0.0,
                    "upstream_area_km2": round(area, 4),
                    "sinuosity": round(length / straight, 3) if straight > 0 else None,
                    "head_elevation_m": round(float(elev_f[r_head[slot]]), 2),
                    "outlet_elevation_m": round(float(elev_f[r_end[slot]]), 2),
                },
                "geometry": {"type": "LineString",
                             "coordinates": [[round(float(x), 6), round(float(y), 6)]
                                             for x, y in coords]},
            })

            hr, hc = divmod(int(r_head[slot]), w)
            nx, ny = _cell_xy(transform, np.array([hr]), np.array([hc]))
            n_up = int(inflow[r_head[slot]])
            node_feats.append({
                "type": "Feature",
                "properties": {
                    "reach_id": slot + 1,
                    "strahler": k,
                    "node_type": ("outlet" if r_down[slot] < 0 else
                                  "junction" if n_up >= 2 else "source"),
                    "n_upstream": n_up,
                    "elevation_m": round(float(elev_f[r_head[slot]]), 2),
                    "upstream_area_km2": round(float(acc_f[r_head[slot]] * cell_area / 1e6), 4),
                },
                "geometry": {"type": "Point",
                             "coordinates": [round(float(nx[0]), 6), round(float(ny[0]), 6)]},
            })

        import os

        base = out_dir or str(TEMP_DIR)
        os.makedirs(base, exist_ok=True)
        crs_name = crs.to_string() if crs is not None else None
        paths = {}
        for key, name, features in (("reaches", "river_network.geojson", feats),
                                    ("nodes", "river_nodes.geojson", node_feats)):
            dest = os.path.join(base, name)
            payload = {"type": "FeatureCollection", "name": key,
                       "crs": {"type": "name", "properties": {"name": crs_name}} if crs_name else None,
                       "features": features}
            with open(dest, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
            paths[key] = dest
        paths["strahler"] = _write_raster(os.path.join(base, "river_strahler.tif"),
                                         order_raster.reshape(h, w), profile)

        # Three independent facts, deliberately not forced to sum to the reach count: a
        # reach can both collect tributaries and leave the tile, and calling that either a
        # junction or an outlet would hide the other half.
        n_outlet = int((r_down < 0).sum())
        n_junction = int((inflow[r_head] >= 2).sum())
        n_head = int((inflow[r_head] == 0).sum())
        warnings = []
        if n_junction == 0:
            warnings.append("no confluence in this tile: the network is a single thread, so "
                            "every reach is order 1 - a larger extent or a lower threshold "
                            "would show the branching structure")
        if n_outlet > 1:
            warnings.append(f"{n_outlet} reaches leave the tile: the network is split by the "
                            f"tile edge (or by internal sinks), so orders are local to this DEM")

        return json.dumps({
            "tool": "ras.river_network",
            "paths": paths,
            "threshold": {"cells": thresh, "area_km2": round(thresh * cell_area / 1e6, 4),
                          "set_by": thresh_by},
            "stats": {
                "reaches": int(r_head.size),
                "junctions": n_junction,
                "outlets": n_outlet,
                "headwaters": n_head,
                "max_strahler": int(strahler.max()),
                "total_length_km": round(total_length / 1000.0, 2),
                "river_cells": int(cells.size),
                "max_upstream_area_km2": round(float(acc_f[r_end].max() * cell_area / 1e6), 3),
            },
            "by_order": {str(k): {"reaches": v["reaches"], "length_km": round(v["length_km"], 2)}
                         for k, v in sorted(by_order.items())},
            "cell_size_m": {"x": float(xres), "y": float(yres), "note": note},
            "shape": [int(h), int(w)],
            "warnings": warnings,
        }, ensure_ascii=False)
    except Exception as e:
        return _error("ras.river_network", e, dem_path=dem_path,
                      min_area_km2=min_area_km2, river_threshold=river_threshold)


@mcp.tool(name="ras.hand", description='''
Description:
Height Above Nearest Drainage (HAND): for every cell, how far it stands above the river it
actually drains into, and - given one or more water stages - how much of the tile would be
flooded. This is the DEM-only route to an inundation map: no hydrograph, no roughness, no
calibration. A cell is counted as flooded when its HAND is below the stage AND it is connected
to the channel, so a low basin behind a ridge is not flooded just for being low.

Parameters:
- dem_path (str): Path to a single-band DEM (GeoTIFF); elevation in metres
- min_area_km2 (float, optional): Cells draining this area count as channel (default 1.0 km2)
- river_threshold (int, optional): Threshold in cells, overrides min_area_km2
- stages (str, optional): Water stages above the bed, e.g. "2,5,8"; omit for HAND alone
- fill (bool, optional): Fill depressions before routing (default True)
- out_dir (str, optional): Directory for the outputs; defaults to the session temp directory

Returns:
- paths (dict): HAND raster, plus one inundation raster per stage
- hand_stats (dict): percentiles of HAND in metres
- stages (list): per stage - flooded cells, area_km2, share of tile, mean and max depth
- curve (list): [stage, area_km2] pairs, ready to plot as a stage-area curve
''')
def ras_hand(dem_path: str, min_area_km2: float = 1.0, river_threshold: Optional[int] = None,
             stages: Optional[str] = None, fill: bool = True,
             out_dir: Optional[str] = None) -> str:
    try:
        if river_threshold is not None and river_threshold < 2:
            raise ValueError("river_threshold must be >= 2 cells")
        if river_threshold is None and min_area_km2 <= 0:
            raise ValueError("min_area_km2 must be positive")

        stage_list: List[float] = []
        for chunk in str(stages or "").replace(";", ",").split(","):
            if chunk.strip():
                val = float(chunk)
                if not val > 0:
                    raise ValueError("every stage must be positive (metres above the channel bed)")
                stage_list.append(val)
        stage_list = sorted(set(stage_list))

        dem, transform, crs, profile = _read_dem(dem_path)
        if not np.isfinite(dem).all():
            dem = np.where(np.isfinite(dem), dem, np.nanmean(dem))
        xres, yres, note = (_cell_size_m(transform, crs) if transform is not None
                            else (1.0, 1.0, "no georeferencing: cell size assumed to be 1 m"))
        cell_area = float(xres * yres)

        if river_threshold is not None:
            thresh, thresh_by = int(river_threshold), "river_threshold"
        else:
            thresh = max(2, int(round(min_area_km2 * 1e6 / cell_area)))
            thresh_by = "min_area_km2"

        filled, direction, acc, order, _raised = _flow_grids(dem, xres, yres, fill, 1e-4)
        h, w = filled.shape
        n = h * w
        target = _downstream_index(direction)
        elev = filled.ravel()
        river = acc.ravel() >= thresh
        if not river.any():
            raise ValueError(
                f"no channel cell at {thresh} cells; lower min_area_km2 or river_threshold")

        # Reference surface: the bed elevation of the channel cell each cell eventually drains
        # into. Walking that with pointer doubling - dest[i] is one step downstream, so
        # dest[dest] is two, then four - converges in log2(path length) vectorised passes
        # instead of one Python iteration per cell. Index n is a sink for cells whose flow
        # path leaves the tile before reaching a channel.
        dest = np.where(river, np.arange(n),
                        np.where(target >= 0, target, n)).astype(np.int64)
        elev_ext = np.r_[elev, np.nan]
        ptr = np.r_[dest, np.int64(n)]
        for _ in range(64):
            nxt = ptr[ptr]
            if np.array_equal(nxt, ptr):
                break
            ptr = nxt
        ref_arr = elev_ext[ptr[:n]]

        hand = np.clip(elev - ref_arr, 0.0, None)
        stray = int(np.isnan(hand).sum())        # no channel downstream inside the tile

        base = out_dir or str(TEMP_DIR)
        import os

        os.makedirs(base, exist_ok=True)
        paths = {"hand": _write_raster(os.path.join(base, "hand.tif"),
                                       np.where(np.isnan(hand), -9999.0, hand).reshape(h, w),
                                       profile)}

        from skimage import measure

        finite = np.isfinite(hand)
        bank = hand[finite]
        hand_stats = {
            "min": 0.0,
            "p10": round(float(np.percentile(bank, 10)), 2),
            "p50": round(float(np.percentile(bank, 50)), 2),
            "p90": round(float(np.percentile(bank, 90)), 2),
            "p99": round(float(np.percentile(bank, 99)), 2),
            "max": round(float(bank.max()), 2),
            "mean": round(float(bank.mean()), 2),
        }

        stage_rows, curve, warnings = [], [], []
        for stage in stage_list:
            low = finite & (hand < stage)
            # Water spreads sideways, not along the flow path, so a low cell only counts when
            # it is in the same connected patch as the channel: label the candidate mask with
            # 8-connectivity and keep the labels that contain at least one river cell.
            lab = measure.label(low.reshape(h, w), connectivity=2).ravel()
            keep = np.unique(lab[river & low])
            wet = np.isin(lab, keep[keep > 0]) & low
            cells = int(wet.sum())
            depth = stage - hand[wet]
            stage_rows.append({
                "stage_m": stage,
                "cells": cells,
                "area_km2": round(cells * cell_area / 1e6, 4),
                "share_of_tile": round(cells / float(n), 4),
                "share_of_valid": round(cells / float(finite.sum()), 4),
                "mean_depth_m": round(float(depth.mean()), 2) if cells else 0.0,
                "max_depth_m": round(float(depth.max()), 2) if cells else 0.0,
                "dropped_unconnected_cells": int(low.sum()) - cells,
            })
            curve.append([stage, round(cells * cell_area / 1e6, 4)])
            paths[f"inundation_{stage:g}m"] = _write_raster(
                os.path.join(base, f"inundation_{stage:g}m.tif"),
                wet.reshape(h, w).astype(np.uint8), profile, dtype="uint8")

        if stray:
            warnings.append(
                f"{stray} cell(s) have no channel downstream inside this tile (edge basins "
                f"below the threshold); they get no HAND value and are left out of the "
                f"inundation masks")
        if stage_list and not any(row["cells"] for row in stage_rows):
            warnings.append("no cell is flooded at these stages: the stages are measured above "
                            "the channel bed, so they need to be larger than the local relief")

        return json.dumps({
            "tool": "ras.hand",
            "paths": paths,
            "threshold": {"cells": thresh, "area_km2": round(thresh * cell_area / 1e6, 4),
                          "set_by": thresh_by},
            "channel_cells": int(river.sum()),
            "hand_stats": hand_stats,
            "stages": stage_rows,
            "curve": curve,
            "cell_size_m": {"x": float(xres), "y": float(yres), "note": note},
            "shape": [int(h), int(w)],
            "warnings": warnings,
        }, ensure_ascii=False)
    except Exception as e:
        return _error("ras.hand", e, dem_path=dem_path, min_area_km2=min_area_km2,
                      river_threshold=river_threshold, stages=stages)


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
