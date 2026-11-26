"""
Terrain server: geomorphometry tools added on top of the upstream DORA tool library.

Three tools, no model weights, no new third-party dependencies beyond what DORA already
ships (numpy / rasterio / scikit-image):

- ``ras.terrain``  — slope, aspect, curvature, TRI, TPI and roughness in one pass
- ``ras.flow``     — depression filling (priority-flood), D8 flow direction, flow accumulation
- ``ras.contour``  — contour lines as GeoJSON

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


def _write_raster(path: str, array: np.ndarray, profile: Optional[dict]) -> str:
    import rasterio

    if profile is None:                      # PNG input: no georeferencing to preserve
        np.save(path + ".npy", array)
        return path + ".npy"
    prof = profile.copy()
    prof.update(count=1, dtype="float32", compress="deflate")
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(array.astype(np.float32), 1)
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

        raised = 0
        filled = dem
        if fill:
            filled, raised = _priority_flood(dem, epsilon)

        direction = _d8_direction(filled, xres, yres)

        # Accumulation: visit cells from the highest filled elevation down. The epsilon
        # gradient guarantees that this is a valid topological order for D8.
        h, w = filled.shape
        acc = np.ones((h, w), dtype=np.float64)
        order = np.argsort(filled, axis=None)[::-1]
        dir_flat = direction.ravel()
        acc_flat = acc.ravel()
        filled_flat = filled.ravel()
        for idx in order:
            code = int(dir_flat[idx])
            if not code:
                continue
            r, c = divmod(int(idx), w)
            dr, dc, _ = next(d for d in _D8 if d[2] == code)
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w:
                nxt = nr * w + nc
                if filled_flat[nxt] <= filled_flat[idx]:
                    acc_flat[nxt] += acc_flat[idx]

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
