"""为每件工具生成一组示例输入 / 示例输出（真跑，不手写）。

    python scripts/build_examples.py             # 全部工具
    python scripts/build_examples.py ras.area    # 只跑指定工具
    python scripts/build_examples.py --list      # 看哪些工具有配方

产物写到 ``examples/<域>/<工具>/``：``input.json``（真实参数）、``output.json``（原样返回）、
``*.webp``（渲染图）、``meta.json``（数据来源 / 图注 / 状态 / 耗时）。
中间文件与夹具在 ``examples/_work``（已 gitignore）。

数据根由 ``DORA_DATA`` 指定，默认 ``D:/research/DORA/data``。
"""
from __future__ import annotations

import importlib
import json
import os
import sys
import time
import traceback
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("DORA_DATA", "D:/research/DORA/data")).expanduser()
EX = REPO / "examples"
WORK = EX / "_work"
FIX = WORK / "fixtures"

_ARGV = [a for a in sys.argv[1:]]
# 工具在 import 时解析 --temp_dir，必须提前改掉 sys.argv
sys.argv = [sys.argv[0], "--temp_dir", str(WORK / "tmp")]
os.environ.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")
sys.path.insert(0, str(REPO / "src"))
os.environ["DORA_DATA"] = str(DATA)

import rasterio  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import dora.tools.analysis as A  # noqa: E402
import dora.tools.calculate as C  # noqa: E402
import dora.tools.model as M  # noqa: E402
import dora.tools.perception as P  # noqa: E402
import dora.tools.poi as O  # noqa: E402
import dora.tools.vis as V  # noqa: E402

MAX_SIDE = 1280
QUALITY = 78

TOOLS = {t["name"]: t for t in json.loads((REPO / "index" / "tools.json").read_text(encoding="utf-8"))}

def E(tool: str):
    """按工具名取真实可调用对象；tools.json 里的 func 名与直觉不一致（如 vec.build_graph → build_road_graph）。"""
    t = TOOLS[tool]
    return getattr(importlib.import_module(f"dora.tools.{t['module']}"), t["func"])

# ---------------------------------------------------------------- 图像工具


def read_bands(path: str | Path) -> np.ndarray:
    with rasterio.open(path) as src:
        return src.read().astype(np.float32)


def to_rgb(arr: np.ndarray, order: tuple[int, ...] = (2, 1, 0),
           ref: float = 60.0, gamma: float = 0.75) -> np.ndarray:
    """灰度世界白平衡 + 统一百分位拉伸；比逐通道拉伸更不容易偏色。"""
    if arr.ndim == 2:
        arr = arr[None]
    if arr.shape[0] == 1:
        x = np.repeat(arr[:1].transpose(1, 2, 0), 3, axis=2)
    else:
        idx = [i for i in order if i < arr.shape[0]][:3]
        x = arr[idx].transpose(1, 2, 0)
        if x.shape[2] == 2:
            x = np.concatenate([x, x[:, :, :1]], axis=2)
    x = x.astype(np.float32).copy()
    for i in range(x.shape[2]):
        denom = np.percentile(x[..., i], ref)
        if denom > 0:
            x[..., i] /= denom
    lo, hi = np.percentile(x, [2, 98])
    x = np.clip((x - lo) / (hi - lo + 1e-6), 0, 1) ** gamma
    return (x * 255).astype(np.uint8)


def to_single(arr: np.ndarray, cmap: str = "inferno") -> np.ndarray:
    v = (arr[0] if arr.ndim == 3 else arr).astype(np.float64)
    # 有 NaN（DEM 空洞、掩膜外区域）时必须用 nan 版分位数，否则整幅会算成同一个值
    lo, hi = np.nanpercentile(v, [2, 98])
    if not np.isfinite(lo) or not np.isfinite(hi) or hi - lo < 1e-12:
        lo, hi = 0.0, 1.0
    n = np.clip((v - lo) / (hi - lo), 0, 1)
    n = np.nan_to_num(n, nan=0.0)
    import matplotlib  # noqa: PLC0415

    return (matplotlib.colormaps[cmap](n)[..., :3] * 255).astype(np.uint8)


def read_mask(path: str | Path) -> np.ndarray:
    with rasterio.open(path) as src:
        return src.read(1)


DAMAGE = {1: (60, 200, 90), 2: (255, 190, 40), 3: (220, 40, 40)}
LANDSLIDE = {255: (255, 120, 0), 1: (255, 120, 0)}
WATER = {1: (60, 160, 255), 255: (60, 160, 255)}
VEG = {1: (80, 200, 80), 5: (60, 180, 60), 6: (30, 140, 30), 255: (60, 180, 60)}


def colorize(mask: np.ndarray, colors: dict[int, tuple[int, int, int]]) -> np.ndarray:
    out = np.zeros((*mask.shape, 3), np.uint8)
    for value, color in colors.items():
        out[mask == value] = color
    return out


def save_webp(img: Image.Image | np.ndarray, out: Path, max_side: int = MAX_SIDE) -> Path:
    if isinstance(img, np.ndarray):
        img = Image.fromarray(img)
    img = img.copy()
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "WEBP", quality=QUALITY, method=6)
    return out


def three_panel(img: np.ndarray, mask: np.ndarray, colors: dict,
                alpha: float = 0.55) -> np.ndarray:
    """左：输入影像；中：掩膜；右：叠加。文字说明写在文档里，不画在图内。"""
    colored = colorize(mask, colors)
    overlay = img.copy()
    hit = colored.sum(axis=2) > 0
    overlay[hit] = (img[hit] * (1 - alpha) + colored[hit] * alpha).astype(np.uint8)
    h, w = img.shape[:2]
    canvas = Image.new("RGB", (w * 3 + 16, h), (255, 255, 255))
    for i, tile in enumerate((img, colored, overlay)):
        canvas.paste(Image.fromarray(tile), (i * (w + 8), 0))
    return np.array(canvas)


def side_by_side(imgs: list[np.ndarray]) -> np.ndarray:
    h = min(i.shape[0] for i in imgs)
    resized = []
    for a in imgs:
        im = Image.fromarray(a)
        if im.height != h:
            im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
        resized.append(im)
    canvas = Image.new("RGB", (sum(i.width for i in resized) + 8 * (len(resized) - 1), h), (255, 255, 255))
    x = 0
    for im in resized:
        canvas.paste(im, (x, 0))
        x += im.width + 8
    return np.array(canvas)


def draw_polygons(img: np.ndarray, geojson_path: str | Path, transform=None,
                  color=(255, 96, 48), width: int = 3) -> np.ndarray:
    """把矢量画到影像上；给了 transform 就按仿射换算，否则按经纬度包围盒拉伸铺满。"""
    gj = json.loads(Path(geojson_path).read_text(encoding="utf-8"))
    canvas = Image.fromarray(img.copy())
    draw = ImageDraw.Draw(canvas)
    h, w = img.shape[:2]

    def px(x, y):
        if transform is not None:
            col, row = ~transform * (x, y)
            return float(col), float(row)
        return x, y

    def walk(geom):
        t, coords = geom["type"], geom["coordinates"]
        if t == "Polygon":
            for ring in coords:
                draw.line([px(x, y) for x, y in ring], fill=color, width=width, joint="curve")
        elif t == "MultiPolygon":
            for poly in coords:
                for ring in poly:
                    draw.line([px(x, y) for x, y in ring], fill=color, width=width, joint="curve")
        elif t == "LineString":
            draw.line([px(x, y) for x, y in coords], fill=color, width=width)
        elif t == "MultiLineString":
            for line in coords:
                draw.line([px(x, y) for x, y in line], fill=color, width=width)
        elif t == "Point":
            cx, cy = px(*coords)
            r = 6
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)

    for feat in gj.get("features", []):
        if feat.get("geometry"):
            walk(feat["geometry"])
    return np.array(canvas)


def render_raster(path: str | Path) -> np.ndarray | None:
    """按内容猜渲染方式：二值/小整数 → 分类色；3 波段以上 → 真彩；单波段 → 色带。"""
    p = Path(path)
    if not p.exists():
        return None
    if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
        return np.array(Image.open(p).convert("RGB"))
    arr = read_bands(p)
    if arr.shape[0] == 1:
        vals = np.unique(arr[0])
        if len(vals) <= 8:
            if set(np.unique(vals).astype(int)) <= {0, 255}:
                return colorize(arr[0].astype(np.uint8), LANDSLIDE)
            return colorize(arr[0].astype(np.uint8), DAMAGE)
        return to_single(arr, "inferno")
    return to_rgb(arr)


# ---------------------------------------------------------------- 夹具


def _crop(path: Path, out: Path, size: int = 1024) -> Path:
    with rasterio.open(path) as src:
        h, w = src.height, src.width
        win = rasterio.windows.Window((w - size) // 2, (h - size) // 2, size, size)
        data = src.read(window=win)
        prof = src.profile.copy()
        prof.update(height=size, width=size, transform=src.window_transform(win))
        with rasterio.open(out, "w", **prof) as dst:
            dst.write(data)
    return out


def _reproject_vec(src: Path, crs: str, out: Path) -> Path:
    if not out.exists():
        import geopandas as gpd  # noqa: PLC0415

        gpd.read_file(src).to_crs(crs).to_file(out, driver="GeoJSON")
    return out


def _write_mask(mask: np.ndarray, ref: Path, out: Path) -> Path:
    with rasterio.open(ref) as src:
        prof = src.profile.copy()
    prof.update(count=1, dtype="uint8", driver="GTiff")
    with rasterio.open(out, "w", **prof) as dst:
        dst.write(mask.astype(np.uint8), 1)
    return out


def fixtures() -> dict[str, Path]:
    """把示例要用的输入准备成固定文件；已存在就复用，避免每次重跑模型。"""
    FIX.mkdir(parents=True, exist_ok=True)
    F: dict[str, Path] = {}
    F["rgb"] = DATA / "images/xbd_agent_benchv1/post/guatemala_volcano_00000004_post.png"
    F["rgb_pre"] = DATA / "images/xbd_agent_benchv1/pre/guatemala_volcano_00000004_pre.png"
    F["flood"] = DATA / "images/disasterm3/libya_flood_agent5/libya_flood_post_4_8.png"
    F["flood_pre"] = DATA / "images/disasterm3/libya_flood_agent5/libya_flood_pre_4_8.png"
    F["flood_sar"] = DATA / "images/disasterm3/libya_flood_agent5/libya_flood_sar_post_4_8.png"
    F["geo"] = DATA / "images/landslide4sense/Japan_all_14_sentinel.tif"
    F["geo_slope"] = DATA / "images/landslide4sense/Japan_all_14_slope.tif"
    F["dem"] = DATA / "images/landslide4sense/Japan_all_14_dem.tif"
    F["reservoir"] = DATA / "images/landslide4sense/reservoir1.tif"
    F["volcano_a"] = DATA / "images/volcano_lava/guatemala_volcano_00000000.png"
    F["volcano_b"] = DATA / "images/volcano_lava/guatemala_volcano_00000004.png"
    F["tokyo"] = DATA / "images/heatisland/09LD1638/image_opt.tif"
    F["mayfield_img"] = DATA / "images/mayfield/region_01/image/20211214_mayfield.tif"

    # 航拍：裁 1024² 给模型用，原图留给坐标换算类
    aerial = FIX / "aerial.tif"
    if not aerial.exists():
        _crop(F["mayfield_img"], aerial, 1024)
    F["aerial"] = aerial

    # 14 波段：12 光谱 + 坡度 + 高程
    geo14 = FIX / "geo14.tif"
    if not geo14.exists():
        E("ras.concat")([str(F["geo"]), str(F["geo_slope"]), str(F["dem"])])
        built = sorted((WORK / "tmp").glob("*concat*.tif"))
        if built:
            built[-1].replace(geo14)
    F["geo14"] = geo14

    # 掩膜：建筑损毁 + 滑坡（各跑一次模型，缓存下来）
    m_damage = FIX / "mask_damage.tif"
    if not m_damage.exists():
        r = json.loads(E("seg.building_damage")(str(F["rgb_pre"]), str(F["rgb"])))
        _write_mask(read_mask(r["mask_path"]), F["rgb"], m_damage)
    F["mask_damage"] = m_damage

    m_land = FIX / "mask_landslide.tif"
    if not m_land.exists():
        r = json.loads(E("seg.landslide_ms")(str(geo14)))
        _write_mask((read_mask(r["mask_path"]) > 0).astype(np.uint8) * 1, geo14, m_land)
    F["mask_landslide"] = m_land

    for cls in (2, 3):
        p = FIX / f"mask_c{cls}.tif"
        if not p.exists():
            _write_mask((read_mask(m_damage) == cls).astype(np.uint8), F["rgb"], p)
        F[f"mask_c{cls}"] = p

    # 矢量：Tokyo OSM 转到栅格坐标系 6677，保证与 image_opt.tif 对得上
    osm = DATA / "images/heatisland/09LD1638/osm"
    F["buildings"] = _reproject_vec(osm / "buildings.geojson", "EPSG:6677", FIX / "buildings.geojson")
    F["landuse"] = _reproject_vec(osm / "landuse.geojson", "EPSG:6677", FIX / "landuse.geojson")
    F["roads"] = _reproject_vec(osm / "roads.geojson", "EPSG:6677", FIX / "roads.geojson")
    F["points"] = _reproject_vec(osm / "points.geojson", "EPSG:6677", FIX / "points.geojson")
    F["poi_utm"] = _reproject_vec(DATA / "images/mayfield/region_01/social_data/poi/pois.geojson",
                                  "EPSG:32616", FIX / "pois_utm.geojson")
    F["poi"] = DATA / "images/disasterm3/noto_earthquake_agent2/noto_earthquake_post_polygon2_poi.geojson"
    F["points_4326"] = DATA / "images/heatisland/09LD1638/osm/points.geojson"

    # OSM 点里带 Timestamp 属性，poi.world_to_pixel 的 json 序列化会直接崩，先只留字符串字段
    pts_clean = FIX / "points_clean.geojson"
    if not pts_clean.exists():
        import geopandas as gpd  # noqa: PLC0415

        g = gpd.read_file(F["points_4326"])
        keep = [c for c in g.columns if c != "geometry" and g[c].map(type).isin([str, int, float]).all()][:3]
        g[keep + ["geometry"]].to_file(pts_clean, driver="GeoJSON")
    F["points_clean"] = pts_clean

    # 点要素裁到栅格范围内：world_to_pixel 遇到范围外的点会算出 inf
    pts_in = FIX / "points_in.geojson"
    if not pts_in.exists():
        import geopandas as gpd  # noqa: PLC0415
        from shapely.geometry import box  # noqa: PLC0415

        with rasterio.open(F["tokyo"]) as src:
            b = src.bounds
        g = gpd.read_file(F["points"])
        g.clip(box(b.left, b.bottom, b.right, b.top)).to_file(pts_in, driver="GeoJSON")
    F["points_in"] = pts_in

    # vec.build_graph 不接受 MultiLineString（shapely 新版会抛错），先炸成单部件
    roads_single = FIX / "roads_single.geojson"
    if not roads_single.exists():
        import geopandas as gpd  # noqa: PLC0415

        import pandas as pd  # noqa: PLC0415

        g = gpd.read_file(F["roads"])
        multi = g.geom_type == "MultiLineString"
        pd.concat([g[~multi], g[multi].explode(index_parts=False)]).to_file(roads_single, driver="GeoJSON")
    F["roads_single"] = roads_single

    roi = FIX / "roi.geojson"
    if not roi.exists():
        import geopandas as gpd  # noqa: PLC0415

        from shapely.geometry import box  # noqa: PLC0415

        g = gpd.read_file(F["buildings"])
        x0, y0, x1, y1 = g.total_bounds
        gpd.GeoDataFrame(geometry=[box(x0 - 20, y0 - 20, (x0 + x1) / 2, y1 + 20)],
                         crs=g.crs).to_file(roi, driver="GeoJSON")
    F["roi"] = roi

    roads_buf = FIX / "roads_buffer.geojson"
    if not roads_buf.exists():
        r = json.loads(E("vec.buffer")(str(F["roads"]), 30.0))
        src = Path(next((v for k, v in r.items() if k.endswith("_path") and isinstance(v, str)), ""))
        if src.exists():
            import shutil  # noqa: PLC0415

            shutil.copy(src, roads_buf)
    F["roads_buffer"] = roads_buf

    # 两个内部同几何的掩膜 + 路网图
    # 保留 build_graph 自己的后缀：repair_min_edges 按后缀判断 GraphML / JSON
    produced = FIX / "graph.graphml"
    if not produced.exists():
        r = json.loads(E("vec.build_graph")(str(roads_single)))
        src = Path(r.get("graph_path") or "")
        if src.exists():
            import shutil  # noqa: PLC0415

            shutil.copy(src, produced)
    F["graph"] = produced
    return F


# ---------------------------------------------------------------- 登记


EXAMPLES: dict[str, dict] = {}


def example(tool: str, status: str = "real"):
    def deco(fn):
        EXAMPLES[tool] = {"fn": fn, "status": status}
        return fn
    return deco


def run_tool(fn, *args, **kwargs) -> dict:
    started = time.time()
    raw = fn(*args, **kwargs)
    elapsed = time.time() - started
    result = json.loads(raw) if isinstance(raw, str) else raw
    if isinstance(result, dict):
        result.setdefault("_example", {})["wall_time_s"] = round(elapsed, 2)
        if isinstance(result.get("_meta"), dict) and "forward_ms" in result["_meta"]:
            result["_meta"] = {"forward_ms": result["_meta"]["forward_ms"]}
        if result.get("error"):
            raise RuntimeError(f"工具返回错误：{result['error']}")
    return result


def first_path(res: dict) -> str | None:
    """从返回里挑第一个真实存在的图片产物（键名各工具不统一：output_path / heatmap_path / slope_path…）。"""
    for key, val in res.items():
        if isinstance(val, str) and key.endswith(("_path", "path")):
            p = Path(val)
            if p.exists() and p.suffix.lower() in (".png", ".tif", ".jpg", ".jpeg", ".webp"):
                return val
    return None


def graph_endpoints(F) -> tuple[list, list]:
    """挑同一连通分量里相距最远的两个节点。

    注意：`vec.graph_shortest_path` 的 start/end 实际按**图节点的坐标系**（这里是与栅格同源的
    世界坐标，且顺序为 (y, x)）解释，docstring 写的是「像素坐标」——按像素传会 snap 失败。
    """
    import xml.etree.ElementTree as ET  # noqa: PLC0415

    import networkx as nx  # noqa: PLC0415

    ns = {"g": "http://graphml.graphdrawing.org/xmlns"}
    root = ET.parse(F["graph"]).getroot()
    keys = {k.get("id"): k.get("attr.name") for k in root.findall(".//g:key", ns)}

    G = nx.Graph()
    for e in root.findall(".//g:edge", ns):
        G.add_edge(e.get("source"), e.get("target"))
    coords: dict[str, tuple] = {}
    for n in root.findall(".//g:node", ns):
        for d in n.findall("g:data", ns):
            if keys.get(d.get("key")) == "xy_json":
                coords[n.get("id")] = tuple(json.loads(d.text))

    with rasterio.open(F["tokyo"]) as src:
        b = src.bounds
    inside = {i: c for i, c in coords.items() if b.left < c[1] < b.right and b.bottom < c[0] < b.top}

    for comp in sorted(nx.connected_components(G), key=len, reverse=True):
        nodes = [inside[i] for i in comp if i in inside]
        if len(nodes) >= 4:
            nodes.sort()
            return list(nodes[0]), list(nodes[-1])
    raise RuntimeError("路网图里没有足够大的连通分量")


def longest_road_pixels(F) -> list[list[int]]:
    """取最长的一条道路中心线，换算成像素折线（给 vis.route_map 当示例路径）。"""
    gj = json.loads(F["roads"].read_text(encoding="utf-8"))
    best, best_len = None, -1
    for feat in gj["features"]:
        geom = feat.get("geometry") or {}
        lines = [geom["coordinates"]] if geom["type"] == "LineString" else geom.get("coordinates", [])
        for line in lines:
            if len(line) > best_len:
                best, best_len = line, len(line)
    with rasterio.open(F["tokyo"]) as src:
        tr = src.transform
    pts = []
    for x, y in best:
        col, row = ~tr * (x, y)
        pts.append([int(row), int(col)])
    return pts[:: max(1, len(pts) // 60)] or pts


def sanitize(obj):
    if isinstance(obj, str):
        for real, tag in ((str(WORK / "tmp"), "<temp_dir>"), (str(DATA), "<DORA_DATA>"),
                          (str(WORK), "<work>"), (str(REPO), "<repo>")):
            obj = obj.replace(real, tag).replace(real.replace("\\", "/"), tag)
        if "<" in obj:
            obj = obj.replace("\\", "/")
        return obj
    if isinstance(obj, list):
        return [sanitize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    return obj


def trim(obj, depth=0):
    if isinstance(obj, list):
        if len(obj) > 3:
            return [trim(x, depth + 1) for x in obj[:3]] + [f"…（共 {len(obj)} 条，此处省略）"]
        return [trim(x, depth + 1) for x in obj]
    if isinstance(obj, dict):
        return {k: trim(v, depth + 1) for k, v in obj.items()}
    return obj


# ---------------------------------------------------------------- 显式配方（需要挑数据 / 串联的）


@example("seg.flood", status="demo")
def ex_flood(F):
    args = {"pre_image_path": str(F["flood_pre"]), "post_image_path": str(F["flood"]), "temp_dir": None}
    args.pop("temp_dir")
    res = run_tool(E("seg.flood"), **args)
    mask = read_mask(res["mask_path"])
    post = to_rgb(read_bands(F["flood"]), (0, 1, 2), ref=55)
    pre = to_rgb(read_bands(F["flood_pre"]), (0, 1, 2), ref=55)
    return dict(args=args, result=res, status="demo",
                figures={"in": side_by_side([pre, post]),
                         "out": three_panel(post, mask, WATER)},
                inputs=["disasterm3/libya_flood_agent5/libya_flood_pre_4_8.png（灾前）",
                        "…/libya_flood_post_4_8.png（灾后，德尔纳洪灾）"],
                caption="上排：灾前｜灾后；下排：灾后影像｜新增淹没（本例为空）｜叠加",
                note="判的是「灾后是水、灾前不是水」的像元。**本例德尔纳的洪水是浑水，光学水体模型零检出**"
                     "（掩膜全黑），与 C2 评测里 IoU 0.107、65% 样本零检出是同一件事；"
                     "要看清能力看 `seg.reservoir`，要稳定的淹没范围先用 SAR 阈值（见 `ras.threshold`）。")


@example("seg.building_damage")
def ex_building(F):
    args = {"pre_image_path": str(F["rgb_pre"]), "post_image_path": str(F["rgb"])}
    res = run_tool(E("seg.building_damage"), **args)
    mask = read_mask(res["mask_path"])
    post = to_rgb(read_bands(F["rgb"]), (0, 1, 2), ref=50)
    pre = to_rgb(read_bands(F["rgb_pre"]), (0, 1, 2), ref=50)
    return dict(args=args, result=res,
                figures={"in": side_by_side([pre, post]),
                         "out": three_panel(post, mask, DAMAGE)},
                inputs=["xbd/guatemala_volcano_00000004_pre.png（0.8 m，1024²）", "…_post.png"],
                caption="上排：灾前｜灾后；下排：灾后影像｜损毁分级（绿=完好、黄=部分、红=完全）｜叠加",
                note="只判「已建成建筑」的损毁等级；两期必须已配准，错位会直接变成假损毁。")


@example("seg.landslide_ms")
def ex_landslide(F):
    args = {"post_image_path": str(F["geo14"])}
    res = run_tool(E("seg.landslide_ms"), **args)
    mask = read_mask(res["mask_path"])
    img = to_rgb(read_bands(F["geo14"]), (2, 1, 0))
    return dict(args=args, result=res,
                figures={"in": img, "out": three_panel(img, mask, LANDSLIDE)},
                inputs=["14 波段影像（ras.concat 的产物，日本山区 1922×1384，10 m）"],
                caption="上：输入影像（假彩色拉伸）；下列：影像｜掩膜｜叠加（橙色为滑坡）",
                note="检出的是裸土/扰动像元，不含体积与危险性；10 m 下小于 30×30 m 的滑坡基本漏检。")


@example("seg.landslide_bitemporal")
def ex_landslide_bt(F):
    args = {"pre_image_path": str(F["rgb_pre"]), "post_image_path": str(F["rgb"])}
    res = run_tool(E("seg.landslide_bitemporal"), **args)
    mask = read_mask(res["mask_path"])
    post = to_rgb(read_bands(F["rgb"]), (0, 1, 2), ref=50)
    return dict(args=args, result=res,
                figures={"out": three_panel(post, mask, LANDSLIDE)},
                inputs=["xbd 灾前 / 灾后影像（0.8 m）——本例用建筑场景代替滑坡，只为演示接口"],
                caption="影像｜双时相滑坡掩膜｜叠加",
                note="双时相模型看的是「两期差异」，与本场景语义不符时输出无意义；真实使用需 0.5–1 m 滑坡影像对。",
                status="demo")


@example("ras.concat")
def ex_concat(F):
    args = {"image_path_list": [str(F["geo"]), str(F["geo_slope"]), str(F["dem"])]}
    res = run_tool(E("ras.concat"), **args)
    return dict(args=args, result=res,
                figures={"out": to_rgb(read_bands(res["output_path"]), (2, 1, 0))},
                inputs=["images/landslide4sense/Japan_all_14_sentinel.tif（12 波段）",
                        "…_slope.tif（坡度）", "…_dem.tif（高程）"],
                caption="拼接后的 14 波段结果（预览取 B4/B3/B2）",
                note="三者的尺寸与地理参考必须完全一致；波段顺序按列表顺序落位，13、14 分别是坡度和高程。")


@example("ras.reproject")
def ex_reproject(F):
    args = {"raster_path": str(F["dem"]), "dst_crs": "EPSG:32654"}
    res = run_tool(E("ras.reproject"), **args)
    return dict(args=args, result=res,
                figures={"in": to_single(read_bands(F["dem"]), "terrain"),
                         "out": to_single(read_bands(res["output_path"]), "terrain")},
                inputs=["images/landslide4sense/Japan_all_14_dem.tif（EPSG:4326，高程米）"],
                caption="上：投影前（经纬度栅格）；下：投影后（UTM 54N，米制像元）",
                note="坡度、缓冲区、最短路这类按「米」算的步骤，都应先投影到米制坐标系。")


@example("ras.slope")
def ex_slope(F):
    proj = WORK / "tmp" / "reprojected.tif"
    if not proj.exists():
        E("ras.reproject")(str(F["dem"]), "EPSG:32654")
    args = {"dem_path": str(proj), "units": "degrees"}
    res = run_tool(E("ras.slope"), **args)
    return dict(args=args, result=res,
                figures={"in": to_single(read_bands(proj), "terrain"),
                         "out": to_single(read_bands(res["slope_path"]), "inferno")},
                inputs=["ras.reproject 输出的 UTM DEM（米制像元 30 m）"],
                caption="上：输入高程；下：坡度（亮=陡，暗=平）",
                note="**必须先投影到米制坐标系**：直接喂经纬度 DEM，像元边长被当成 0.000129（度），"
                     "坡度均值会算成 86°，不报错但全错。")


@example("ras.hillshade")
def ex_hillshade(F):
    args = {"dem_path": str(F["dem"]), "azimuth": 315, "altitude": 45}
    res = run_tool(E("ras.hillshade"), **args)
    path = next((res[k] for k in res if k.endswith("_path") and res[k]), None)
    return dict(args=args, result=res,
                figures={"out": to_single(read_bands(path), "gray")} if path else {},
                inputs=["images/landslide4sense/Japan_all_14_dem.tif"],
                caption="山体阴影（315° 方位、45° 高度角）",
                note="只影响观感，不改变高程；做地形晕渲或叠加专题图时用。")


def _proj_dem(F) -> Path:
    """投影到 UTM 54N 的 DEM；坡向、汇流、等高线这类按米算的工具都用它。"""
    proj = WORK / "tmp" / "reprojected.tif"
    if not proj.exists():
        E("ras.reproject")(str(F["dem"]), "EPSG:32654")
    return proj


def _grid(panels: list[tuple[str, np.ndarray]], cols: int = 3) -> np.ndarray:
    """带标题的等宽拼图，用来一次展示多个派生量。"""
    tiles = []
    for title, rgb in panels:
        im = Image.fromarray(rgb)
        im.thumbnail((420, 420), Image.LANCZOS)
        canvas = Image.new("RGB", (im.width, im.height + 20), (255, 255, 255))
        canvas.paste(im, (0, 20))
        ImageDraw.Draw(canvas).text((6, 4), title, fill=(25, 25, 25))
        tiles.append(canvas)
    tw = max(t.width for t in tiles)
    th = max(t.height for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (tw * cols + 8 * (cols - 1), th * rows + 8 * (rows - 1)), (255, 255, 255))
    for i, t in enumerate(tiles):
        out.paste(t, ((i % cols) * (tw + 8), (i // cols) * (th + 8)))
    return np.array(out)


@example("ras.terrain")
def ex_terrain(F):
    proj = _proj_dem(F)
    attrs = "slope,aspect,curvature,tri,tpi,roughness"
    args = {"dem_path": str(proj), "attributes": attrs, "units": "degrees"}
    res = run_tool(E("ras.terrain"), **args)
    # 曲率与 TPI 以 0 为中心，用「零值偏暗」的发散色带，平地才不会糊成一片白
    cmaps = {"slope": "inferno", "aspect": "hsv", "curvature": "berlin",
             "tri": "viridis", "tpi": "berlin", "roughness": "magma"}
    titles = {"slope": "slope (deg)", "aspect": "aspect (deg from N)", "curvature": "curvature (1/100m)",
              "tri": "TRI", "tpi": "TPI", "roughness": "roughness (m)"}
    def enhance(a: np.ndarray) -> np.ndarray:
        """曲率与 TPI 绝大多数像元贴着 0，直接线性拉伸会一片灰；先做符号平方根。"""
        return np.sign(a) * np.sqrt(np.abs(a))

    panels = []
    for k in attrs.split(","):
        band = read_bands(res["paths"][k])
        if k in ("curvature", "tpi"):
            band = enhance(band)
        panels.append((titles[k], to_single(band, cmaps[k])))
    return dict(args=args, result=res,
                figures={"in": to_single(read_bands(proj), "terrain"),
                         "out": _grid(panels)},
                inputs=["ras.reproject 输出的 UTM DEM（12 m 像元，日本山区整景）"],
                caption="上：输入高程；下：一次算出的 6 个地形因子",
                note="与 `ras.slope` 的关键差别：这里按**米**算，并在内部把经纬度的度换算成米；"
                     "坡度用 Horn 3×3（同 GDAL gdaldem），曲率用 Zevenbergen–Thorne，TRI 用 Riley。")


def _flow_crop(F) -> Path:
    """900x900 子区；汇流与流域两件工具共用同一块地形，示例之间可以对照。"""
    proj = _proj_dem(F)
    crop = WORK / "tmp" / "dem_flow_crop.tif"
    if not crop.exists():
        with rasterio.open(proj) as src:
            win = rasterio.windows.Window(400, 400, 900, 900)
            data = src.read(1, window=win)
            prof = src.profile.copy()
            prof.update(height=900, width=900, transform=src.window_transform(win))
        with rasterio.open(crop, "w", **prof) as dst:
            dst.write(data, 1)
    return crop


GEOM_COLORS = {1: (232, 230, 223), 2: (150, 40, 40), 3: (198, 74, 44), 4: (226, 145, 60),
               5: (240, 196, 120), 6: (176, 196, 158), 7: (110, 190, 165), 8: (140, 175, 215),
               9: (48, 105, 175), 10: (20, 45, 90)}


def _geom_overlay(cls: np.ndarray, shade: np.ndarray, dim: float = 0.22) -> np.ndarray:
    """地貌分类上色后压一层山影，类别之外（0）保持黑色。"""
    rgb = np.zeros((*cls.shape, 3), np.uint8)
    for k, c in GEOM_COLORS.items():
        rgb[cls == k] = c
    out = (rgb * (1 - dim) + shade[..., None] * dim).astype(np.uint8)
    out[cls == 0] = 0
    return out


def _shade_of(path: Path) -> np.ndarray:
    hs = json.loads(E("ras.hillshade")(str(path), 315, 45))
    hs_path = next(v for k, v in hs.items() if k.endswith("_path") and v)
    return to_single(read_bands(hs_path), "gray")[..., 0]      # 灰度单通道，供叠加用


@example("ras.geomorphons")
def ex_geomorphons(F):
    crop = _flow_crop(F)
    shade = _shade_of(crop)

    out10 = WORK / "tmp" / "geom10"
    out30 = WORK / "tmp" / "geom30"
    args = {"dem_path": str(crop), "search_distance": 10, "flatness_deg": 1.0,
            "out_dir": str(out10)}
    res = run_tool(E("ras.geomorphons"), **args)
    res30 = run_tool(E("ras.geomorphons"), dem_path=str(crop), search_distance=30,
                     flatness_deg=1.0, out_dir=str(out30))

    cls10 = read_bands(res["path"])[0].astype(int)
    cls30 = read_bands(res30["path"])[0].astype(int)

    top = sorted(res["share"].items(), key=lambda kv: -kv[1])[:3]
    panels = [("hillshade", shade),
              ("geomorphons, search 10 cells", _geom_overlay(cls10, shade)),
              ("geomorphons, search 30 cells", _geom_overlay(cls30, shade))]
    return dict(args=args, result=res,
                figures={"in": to_single(read_bands(crop), "terrain"), "out": _grid(panels)},
                inputs=["同一块 900×900 子区（EPSG:32654，像元 12 m），两个搜索半径"],
                caption=(f"中：10 格（约 120 m）尺度，坡面 "
                         f"{res['share']['slope'] * 100:.0f}%、谷 {res['share']['valley'] * 100:.1f}%；"
                         f"右：30 格（约 360 m）尺度，同一地形被归并成更大的单元"),
                note=("地貌分类没有「正确答案」，只有「什么尺度上的答案」：`search_distance` 定多大，"
                      f"被认作脊和谷的东西就多大。这张图里 10 格尺度下前三类是 "
                      f"{'、'.join(k for k, _ in top)}；放到 30 格，支沟被合并，坡面比例上升、"
                      "谷和脊的位置往外移。换个尺度再跑一遍，是这类工具的正确用法。"))


def _fixed_rgb(v: np.ndarray, cmap: str, lo: float, hi: float,
               gamma: float = 1.0) -> np.ndarray:
    """固定值域上色：指数类要能对着色标读数值，不能按百分位拉伸。

    gamma > 1 把大段低值压到接近背景色，只让真正高出阈值的部分显色——NDWI 用它把地面纹理
    压掉、只留水面。
    """
    import matplotlib  # noqa: PLC0415
    n = np.nan_to_num(np.clip((v - lo) / (hi - lo), 0, 1)) ** gamma
    return (matplotlib.colormaps[cmap](n)[..., :3] * 255).astype(np.uint8)


@example("ras.index")
def ex_index(F):
    src = F["geo"]                                   # 12 波段 Sentinel-2：B1..B12
    out_dir = WORK / "tmp"
    args = {"image_path": str(src), "band_a": 8, "band_b": 4, "name": "ndvi",
            "out_path": str(out_dir / "ndvi.tif")}
    res = run_tool(E("ras.index"), **args)
    ndvi = read_bands(res["out_path"])[0]

    # 同一景再算一次 NDWI，只换波段号
    ndwi_res = run_tool(E("ras.index"), image_path=str(src), band_a=3, band_b=8,
                        name="ndwi", out_path=str(out_dir / "ndwi.tif"))
    ndwi = read_bands(ndwi_res["out_path"])[0]

    rgb = to_rgb(read_bands(src), order=(3, 2, 1))   # B4 / B3 / B2 真彩

    panels = [("true colour (B4 / B3 / B2)", rgb),
              ("NDVI = (B8-B4)/(B8+B4)", _fixed_rgb(ndvi, "RdYlGn", -0.3, 0.9)),
              ("NDWI = (B3-B8)/(B3+B8)", _fixed_rgb(ndwi, "Blues", -0.6, 0.1, gamma=3.0))]
    st = res["stats"]
    return dict(args=args, result=res,
                figures={"in": rgb, "out": _grid(panels)},
                inputs=["同一景 12 波段 Sentinel-2（EPSG:4326，1384×1922）；波段按 B1..B12 排列"],
                caption=(f"NDVI 中位 {st['p50']:+.2f}（p5 {st['p5']:+.2f} ~ p95 {st['p95']:+.2f}），"
                         f"NDWI 中位 {ndwi_res['stats']['p50']:+.2f}；负 NDVI 只占 "
                         f"{st['share_negative'] * 100:.1f}% 的像元"),
                note=("归一化差值只做一件事：`(A−B)/(A+B)`，所以它**对量纲免疫**——数字量（DN）和反射率算出来"
                      "完全一样，不需要逐景定标。这也是它比阈值法稳的原因。"
                      "换指数就是换波段号：NDVI 用 (NIR, 红)，NDWI 用 (绿, NIR)，NDMI 用 (NIR, SWIR1)，"
                      "NBR 用 (NIR, SWIR2)。"
                      "请注意波段号是**按数据源的排法**给的，不是按卫星波段名——这块数据是 B1..B12 顺序，"
                      f"所以 B8 是第 8 个。算出来负 NDVI 的那 {st['share_negative'] * 100:.1f}% 像元是水面、"
                      "阴影和云，正好可以和淹没范围对照。"))


@example("ras.flow")
def ex_flow(F):
    crop = _flow_crop(F)

    args = {"dem_path": str(crop), "river_threshold": 800}
    res = run_tool(E("ras.flow"), **args)
    acc = read_bands(res["paths"]["flow_accumulation"])
    filled = read_bands(res["paths"]["filled"]) if "filled" in res["paths"] else read_bands(crop)
    river = read_bands(res["paths"]["river"]) if "river" in res["paths"] else None
    base = to_single(filled, "terrain")
    if river is not None:
        base = base.copy()
        base[river[0] > 0] = (60, 170, 255)
    panels = [("filled DEM + river", base),
              ("log10 flow accumulation", to_single(np.log10(acc + 1.0), "inferno"))]
    return dict(args=args, result=res,
                figures={"in": to_single(read_bands(crop), "terrain"), "out": _grid(panels, cols=2)},
                inputs=["同一 DEM 的 900×900 子区（EPSG:32654）"],
                caption="左：填洼后的地形，蓝色为汇流量 ≥800 的河段；右：汇流累积（对数）",
                note="先填洼再定流向：不填洼的话，每一个小坑都会变成假的水系断点。"
                     "给定出水口用同样的汇流面反查，就是流域边界。")


@example("ras.catchment")
def ex_catchment(F):
    crop = _flow_crop(F)
    with rasterio.open(crop) as src:
        tr = src.transform

    # 出口不是猜的：先算汇流面，取累积量最大的那一格（全图主河道最下游）。
    flow = run_tool(E("ras.flow"), dem_path=str(crop), river_threshold=4000)
    acc = read_bands(flow["paths"]["flow_accumulation"])[0]
    r0, c0 = np.unravel_index(int(np.argmax(acc)), acc.shape)
    x, y = tr * (c0 + 0.5, r0 + 0.5)

    args = {"dem_path": str(crop), "pour_points": f"{x:.2f},{y:.2f}",
            "pour_crs": "same", "simplify_m": 30.0}
    res = run_tool(E("ras.catchment"), **args)
    o = res["outlets"][0]

    hs = json.loads(E("ras.hillshade")(str(crop), 315, 45))
    hs_path = next((v for k, v in hs.items() if k.endswith("_path") and v), None)
    shade = to_single(read_bands(hs_path), "gray") if hs_path else to_single(read_bands(crop), "terrain")

    lab = read_bands(res["paths"]["catchment"])[0]
    basin = lab > 0
    gj = res["paths"]["catchment_geojson"]

    # 左：河网 + 出口。流域在这里占了 86%，轮廓几乎等于图幅边，画出来信息量不如河网。
    left = to_single(read_bands(crop), "terrain")
    if "river" in flow["paths"]:
        riv = read_bands(flow["paths"]["river"])[0] > 0
        left = left.copy()
        left[riv] = (70, 165, 255)
    li = Image.fromarray(left)
    orow, ocol = o["pixel"]                      # 用工具自己回报的落格，不反算仿射
    ImageDraw.Draw(li).ellipse([ocol - 11, orow - 11, ocol + 11, orow + 11],
                               fill=(245, 70, 55), outline=(255, 255, 255), width=3)
    left = np.array(li)

    mid = to_single(np.log10(acc + 1.0), "inferno")

    tint = shade.copy()
    tint[basin] = (shade[basin] * 0.55 + np.array([80, 140, 245]) * 0.45).astype(np.uint8)
    right = draw_polygons(tint, gj, tr, color=(255, 255, 255), width=6)
    right = draw_polygons(right, gj, tr, color=(240, 70, 55), width=2)

    panels = [("river network, red dot = outlet", left),
              ("log10 flow accumulation", mid),
              ("catchment (blue) over hillshade", right)]
    tr_ = res["truncation"]
    return dict(args=args, result=res,
                figures={"in": to_single(read_bands(crop), "terrain"), "out": _grid(panels)},
                inputs=["同一块 900×900 子区（EPSG:32654，像元 12 m）；出水口取汇流面的最大值格"],
                caption=(f"流域 {o['area_km2']:.1f} km²（占图幅 {o['share_of_tile'] * 100:.0f}%），"
                         f"出口在{'图幅边界' if tr_['outlet_on_border'] else '图幅内部'}；"
                         f"{tr_['border_cells']} 格触边"),
                note=("出口坐标由 `ras.flow` 的汇流面给出：累积量最大的一格就是本图主河道最下游，"
                      "沿河道往上游反查就是流域。这里出口正好落在图幅左边界，"
                      "所以面积是**下界**——左边界外还有上游未计入。"))


RIV_COLORS = {1: (108, 176, 232), 2: (46, 122, 210), 3: (246, 176, 64),
              4: (232, 74, 58), 5: (168, 70, 150)}
RIV_WIDTH = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}


def _order_chart(by_order: dict) -> np.ndarray:
    """按级数统计长度与段数：一级最多但最碎，能一眼看出「级数跳得慢」。"""
    import matplotlib  # noqa: PLC0415
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415

    ks = sorted(int(k) for k in by_order)
    lens = [by_order[str(k)]["length_km"] for k in ks]
    cnts = [by_order[str(k)]["reaches"] for k in ks]
    fig, ax = plt.subplots(figsize=(4.2, 4.2), dpi=100)
    bars = ax.barh([f"order {k}" for k in ks], lens,
                   color=[tuple(c / 255 for c in RIV_COLORS.get(k, (200, 200, 200))) for k in ks],
                   edgecolor="#22303f", linewidth=0.7)
    for bar, k, c, L in zip(bars, ks, cnts, lens):
        ax.text(L + max(lens) * 0.02, bar.get_y() + bar.get_height() / 2,
                f"n={c}   {L:.1f} km", va="center", fontsize=7.5, color="#22303f")
    ax.set_xlim(0, max(lens) * 1.5)
    ax.set_xlabel("total length (km)", fontsize=8)
    ax.tick_params(labelsize=8)
    ax.invert_yaxis()
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    fig.canvas.draw()
    out = np.asarray(fig.canvas.buffer_rgba())[..., :3].copy()
    plt.close(fig)
    return out


def _draw_reaches(img: np.ndarray, feats: list, tr, halo: bool = True) -> np.ndarray:
    """按 Strahler 级数上色加粗；先描一圈深色，浅色一级在雪地/天空背景上也看得见。"""
    canvas = Image.fromarray(img.copy())
    draw = ImageDraw.Draw(canvas)
    for f in feats:
        pr = f["properties"]
        pts = [tuple(float(v) for v in (~tr * (x, y))) for x, y in f["geometry"]["coordinates"]]
        if len(pts) < 2:
            continue
        col = RIV_COLORS.get(pr["strahler"], (255, 255, 255))
        wdt = RIV_WIDTH.get(pr["strahler"], 2)
        if halo:
            draw.line(pts, fill=(18, 28, 42), width=wdt + 2, joint="curve")
        draw.line(pts, fill=col, width=wdt, joint="curve")
    return np.array(canvas)


@example("ras.river_network")
def ex_river_network(F):
    crop = _flow_crop(F)
    with rasterio.open(crop) as src:
        tr = src.transform

    args = {"dem_path": str(crop), "min_area_km2": 0.5, "simplify_m": 5.0}
    res = run_tool(E("ras.river_network"), **args)
    feats = json.loads(Path(res["paths"]["reaches"]).read_text(encoding="utf-8"))["features"]
    nodes = json.loads(Path(res["paths"]["nodes"]).read_text(encoding="utf-8"))["features"]
    shade = np.repeat(_shade_of(crop)[..., None], 3, axis=2)      # 灰度 -> RGB，供彩色描线

    left = _draw_reaches(shade, feats, tr)

    # 中：节点。汇流点按上游面积给半径，出图口画成方块——它们提示「这里的级数只是图幅内的」
    right = _draw_reaches(shade, feats, tr, halo=False)
    canvas = Image.fromarray(right.copy())
    draw = ImageDraw.Draw(canvas)
    for f in nodes:
        pr = f["properties"]
        px, py = (float(v) for v in (~tr * tuple(f["geometry"]["coordinates"])))
        if pr["node_type"] == "outlet":
            draw.rectangle([px - 7, py - 7, px + 7, py + 7],
                           fill=(238, 60, 48), outline=(255, 255, 255), width=2)
        else:
            r = 3.5 + 3.0 * np.log10(pr["upstream_area_km2"] + 1.0)
            draw.ellipse([px - r, py - r, px + r, py + r],
                         fill=(255, 246, 214), outline=(30, 40, 55), width=2)
    right = np.array(canvas)

    st = res["stats"]
    panels = [("reaches by Strahler order", left),
              ("nodes: junctions (circles), outlets (squares)", right),
              ("length and reach count by order", _order_chart(res["by_order"]))]
    return dict(args=args, result=res,
                figures={"in": to_single(read_bands(crop), "terrain"), "out": _grid(panels)},
                inputs=["同一块 900×900 子区（EPSG:32654，像元 12 m）；阈值 0.5 km² 汇水面积"],
                caption=(f"{st['reaches']} 条河段、共 {st['total_length_km']:.0f} km，最高 "
                         f"{st['max_strahler']} 级；{st['junctions']} 个汇流点、"
                         f"{st['outlets']} 处水流出图"),
                note=("级数不是随便编号：两条一级支流汇成才升到二级，一条一级并入二级仍是二级——"
                      "只有**两条同级的汇合**才会加一，所以数字跳得很慢，4 级已经代表整幅图的主干。"
                      f"`magnitude` 是另一个口径（Shreve）：数上游有几条源头，出口处为 {st['headwaters']}，"
                      "更能反映「汇集了多少条沟」。注意右下方的方块：水从这里流出图幅，"
                      "边界外的上游没算进来，级数只在图幅内成立。"))


HAND_STAGES = (2, 5, 10, 20)
HAND_COLORS = {2: (24, 88, 168), 5: (60, 142, 216), 10: (128, 194, 240), 20: (198, 226, 250)}


def _curve_chart(curve: list) -> np.ndarray:
    """水位–面积曲线：预警要的就是这张图（涨到几米、淹多大）。"""
    import matplotlib  # noqa: PLC0415
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415

    stage = [c[0] for c in curve]
    area = [c[1] for c in curve]
    fig, ax = plt.subplots(figsize=(4.2, 4.2), dpi=100)
    ax.plot(area, stage, "-o", color="#1d5fa8", linewidth=2, markersize=5,
            markerfacecolor="white", markeredgewidth=1.6)
    for a, s_ in zip(area, stage):
        ax.annotate(f"{a:.1f}", (a, s_), textcoords="offset points", xytext=(6, 4), fontsize=7.5,
                    color="#22303f")
    ax.set_xlabel("flooded area (km²)", fontsize=8)
    ax.set_ylabel("water stage (m)", fontsize=8)
    ax.tick_params(labelsize=8)
    ax.set_xlim(0, max(area) * 1.25)
    ax.set_ylim(0, max(stage) * 1.15)
    ax.grid(True, color="#d8dee6", linewidth=0.6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    fig.canvas.draw()
    out = np.asarray(fig.canvas.buffer_rgba())[..., :3].copy()
    plt.close(fig)
    return out


@example("ras.hand")
def ex_hand(F):
    crop = _flow_crop(F)
    args = {"dem_path": str(crop), "min_area_km2": 0.5,
            "stages": ",".join(str(s) for s in HAND_STAGES)}
    res = run_tool(E("ras.hand"), **args)

    hand = read_bands(res["paths"]["hand"])[0].astype(float)
    shade = np.repeat(_shade_of(crop)[..., None], 3, axis=2)

    # 左：HAND 本身。0 = 河道，往上越远离河道；nodata 涂灰。
    left = to_single(np.clip(hand, 0, 30), "YlGnBu_r")
    left[hand < 0] = (232, 232, 232)

    # 中：逐级叠色，大水位先画、小水位后画，得到嵌套的淹没带
    mid = shade.copy()
    for stage in sorted(HAND_STAGES, reverse=True):
        wet = read_bands(res["paths"][f"inundation_{stage}m"])[0] > 0
        col = np.array(HAND_COLORS[stage])
        mid[wet] = (shade[wet] * 0.22 + col * 0.78).astype(np.uint8)
    mid = mid.copy()

    st = res["stages"]
    panels = [("HAND: metres above nearest drainage", left),
              ("inundation at 2 / 5 / 10 / 20 m stage", mid),
              (f"stage-area curve (channel = {res['threshold']['area_km2']:g} km2)", _curve_chart(res["curve"]))]
    biggest, smallest = st[-1], st[0]
    return dict(args=args, result=res,
                figures={"in": to_single(read_bands(crop), "terrain"), "out": _grid(panels)},
                inputs=["同一块 900×900 子区（EPSG:32654，像元 12 m）；河道取汇水面积 0.5 km² 以上"],
                caption=(f"{res['channel_cells']} 格河道；水位 {smallest['stage_m']:g} m 淹 "
                         f"{smallest['area_km2']:.1f} km²（{smallest['share_of_tile'] * 100:.1f}%），"
                         f"{biggest['stage_m']:g} m 淹 {biggest['area_km2']:.1f} km²"
                         f"（{biggest['share_of_tile'] * 100:.1f}%）"),
                note=("左图是 HAND——每个格子「高出它最终汇入的那条河道多少米」，所以它天生就是淹没深度："
                      "水位涨到 5 m，HAND < 5 的地方就是水面。中图正是这条规则逐级套上去的结果，"
                      "越靠河道越先淹、淹得越深。"
                      "这里的水位是**相对河底**的，不是绝对高程；要换成河道水位站读数，把站的水位减去"
                      "该河段河底高程即可。另有一部分格子没有 HAND 值（涂灰）：它们的水流在图幅外"
                      "才汇入河道，本图里看不见那条河，只能留空——这也是为什么面积是「至少」而不是「正好」。"
                      "这套方法是筛查级：静水面、无流速、看不见桥涵和堤防，河漫滩准，平原城区偏大。"))


@example("ras.wetness")
def ex_wetness(F):
    crop = _flow_crop(F)
    args = {"dem_path": str(crop), "indices": "twi,spi,sti", "min_slope_deg": 0.1}
    res = run_tool(E("ras.wetness"), **args)
    twi = read_bands(res["paths"]["twi"])[0]
    spi = read_bands(res["paths"]["spi"])[0]
    sti = read_bands(res["paths"]["sti"])[0]

    panels = [("TWI = ln(a / tan b): wetness", to_single(twi, "YlGnBu")),
              ("SPI = ln(a * tan b): stream power", to_single(spi, "YlOrRd")),
              ("STI: sediment transport", to_single(sti, "magma"))]
    return dict(args=args, result=res,
                figures={"in": to_single(read_bands(crop), "terrain"), "out": _grid(panels)},
                inputs=["同一块 900×900 子区（EPSG:32654，像元 12 m）"],
                caption=(f"TWI 中位 {res['stats']['twi']['p50']:.1f}（p95 {res['stats']['twi']['p95']:.1f}），"
                         f"SPI 中位 {res['stats']['spi']['p50']:.1f}；"
                         f"{res['params']['cells_at_slope_floor']} 格触到坡度下限"),
                note=("三个指数共用两个输入：汇流面积 a（每单位等高线宽度的上游面积，单位米）和坡度 β，"
                      "所以一次算完最省。分工是：**TWI 看「水在哪积」**（蓝色沿沟谷），"
                      "**SPI 看「水在哪冲」**（红色沿陡沟），**STI 看「泥沙往哪走」**。"
                      "TWI 是相对量，同一景内可比、跨景不可比——它的绝对值取决于 a 的定义（这里用 a = 格数 × 格宽）。"
                      "平地会触发 `min_slope_deg` 下限，此时指数由下限而非地形决定，工具会回报触限格数。"))


@example("ras.contour")
def ex_contour(F):
    proj = _proj_dem(F)
    args = {"dem_path": str(proj), "interval": 100.0}
    res = run_tool(E("ras.contour"), **args)

    hs = json.loads(E("ras.hillshade")(str(proj), 315, 45))
    hs_path = next((v for k, v in hs.items() if k.endswith("_path") and v), None)
    base = to_single(read_bands(hs_path), "gray") if hs_path else to_single(read_bands(proj), "gray")
    img = Image.fromarray(base).convert("RGB")
    draw = ImageDraw.Draw(img)
    gj = json.loads(Path(res["out_path"]).read_text(encoding="utf-8"))
    with rasterio.open(proj) as src:
        inv = ~src.transform
    for feat in gj["features"]:
        pts = [tuple(inv * (x, y)) for x, y in feat["geometry"]["coordinates"]]
        if len(pts) > 1:
            draw.line([(c, r) for c, r in pts], fill=(220, 40, 40), width=2)
    return dict(args=args, result=res,
                figures={"in": to_single(read_bands(proj), "terrain"), "out": np.array(img)},
                inputs=["UTM DEM（12 m），等高距 100 m"],
                caption=f"红线为等高线：{res['n_lines']} 条、总长 {res['total_length_m'] / 1000:.0f} km",
                note="输出是 GeoJSON，每条线带 `elevation`，可直接进 QGIS/ArcGIS 或叠加到专题图上。")


@example("ras.vectorize")
def ex_vectorize(F):
    args = {"mask_path": str(F["mask_damage"]), "classes": [2, 3], "pixel_size_m": 0.8}
    res = run_tool(E("ras.vectorize"), **args)
    post = to_rgb(read_bands(F["rgb"]), (0, 1, 2), ref=50)
    with rasterio.open(F["rgb"]) as src:
        tr = src.transform
    return dict(args=args, result=res,
                figures={"in": post, "out": draw_polygons(post, res["vector_path"], tr)},
                inputs=["seg.building_damage 掩膜（类别 2、3）"],
                caption="上：灾后影像；下：矢量化后的建筑轮廓（橙线，26 个面）",
                note="相邻像元会合并成一个面；细碎图斑建议接 `vec.filter_by_area` 清理。")


@example("vis.damage_map")
def ex_damage_map(F):
    out = WORK / "damage_map.png"
    args = {"base_image_path": str(F["rgb"]), "overlay_mask_path": str(F["mask_damage"]),
            "output_path": str(out), "pixel_size_m": 0.8,
            "title": "Guatemala Volcano - Building Damage",
            "class_labels": {"1": "Intact", "2": "Partial", "3": "Destroyed"}, "alpha": 0.45}
    res = run_tool(E("vis.damage_map"), **args)
    return dict(args=args, result=res,
                figures={"in": to_rgb(read_bands(F["rgb"]), (0, 1, 2), ref=50), "out": out},
                inputs=["xbd 灾后影像（0.8 m）", "seg.building_damage 掩膜"],
                caption="成品专题图：标题、图例、指北针、比例尺齐全",
                note="`pixel_size_m` 只影响比例尺，不改变叠加几何；不传就没有比例尺。")


@example("vis.overlay_mask")
def ex_overlay(F):
    out = WORK / "overlay.png"
    args = {"image_path": str(F["rgb"]), "mask_path": str(F["mask_damage"]),
            "output_path": str(out), "alpha": 0.5,
            "class_labels": {"1": "Intact", "2": "Partial", "3": "Destroyed"}}
    res = run_tool(E("vis.overlay_mask"), **args)
    return dict(args=args, result=res, figures={"out": out},
                inputs=["xbd 灾后影像", "损毁掩膜"],
                caption="纯叠加图（无图例/指北针），比 `vis.damage_map` 轻",
                note="要出正式图用 `vis.damage_map`；这个用于快速目视核对。")


@example("vis.before_after_panel")
def ex_before_after(F):
    out = WORK / "before_after.png"
    args = {"pre_image_path": str(F["rgb_pre"]), "post_image_path": str(F["rgb"]),
            "output_path": str(out), "title": "Guatemala Volcano"}
    res = run_tool(E("vis.before_after_panel"), **args)
    return dict(args=args, result=res, figures={"out": out},
                inputs=["同一地点的灾前、灾后影像"],
                caption="左右对照图，用于人工核对变化",
                note="工具不做配准，错位会直接体现在图面上。")


@example("vis.temporal_panel")
def ex_temporal(F):
    out = WORK / "temporal.png"
    seq = sorted((DATA / "images/multi_temp/hurricane_florence_00000110").glob("*.png"))[:4]
    if not seq:
        seq = sorted((DATA / "images/multi_temp").glob("*/*.png"))[:4]
    args = {"image_paths": [str(p) for p in seq], "output_path": str(out),
            "labels": [p.parent.name[-3:] + "h" for p in seq],
            "title": "Hurricane Florence - Temporal Comparison"}
    res = run_tool(E("vis.temporal_panel"), **args)
    return dict(args=args, result=res, figures={"out": out},
                inputs=["multi_temp 下同一地点 4 个时刻的影像"],
                caption="时序拼图（每列一个时刻）",
                note="适合展示淹没范围扩张、植被恢复这类随时间变化的场景。")


@example("vis.route_map", status="demo")
def ex_route(F):
    path = longest_road_pixels(F)
    out = WORK / "route.png"
    args = {"base_image_path": str(F["tokyo"]), "path_pixels": path,
            "pixel_size_m": 0.2, "title": "Evacuation Route"}
    res = run_tool(E("vis.route_map"), **args)
    out = first_path(res)
    return dict(args=args, result=res, figures={"out": out} if out else {},
                inputs=["Tokyo OSM 最长一条道路中心线（换算成像素折线）+ 同区域影像"],
                caption="把一条路径画在底图上（默认青色）；本例用道路中心线代替最短路",
                note="**示意**：`vec.build_graph` 建出的图被切得很碎（300 个节点、最大连通分量只有 44），"
                     "最短路只有几十像素，画出来没意义，所以这里用真实道路几何代替。"
                     "`path_pixels` 是像素坐标，可直接叠到同尺寸底图上。")


@example("vis.report_page")
def ex_report(F):
    map_png = WORK / "damage_map.png"
    if not map_png.exists():
        E("vis.damage_map")(base_image_path=str(F["rgb"]), overlay_mask_path=str(F["mask_damage"]),
                         output_path=str(map_png), pixel_size_m=0.8,
                         title="Building Damage", class_labels={"1": "Intact", "2": "Partial", "3": "Destroyed"})
    chart_png = WORK / "bar.png"
    if not chart_png.exists():
        mask = read_mask(F["mask_damage"])
        E("vis.bar_chart")(data={"intact": int((mask == 1).sum()), "partial": int((mask == 2).sum()),
                              "destroyed": int((mask == 3).sum())},
                        output_path=str(chart_png), title="Damage by Class")
    out = WORK / "report.png"
    args = {"map_image_path": str(map_png), "chart_image_path": str(chart_png),
            "output_path": str(out), "title": "Guatemala Volcano - Situation Report",
            "summary_text": "Partial damage dominates; 2,073 pixels classified as destroyed.",
            "key_statistics": {"destroyed_px": 2073, "partial_px": 25880, "area_km2": 1.7}}
    res = run_tool(E("vis.report_page"), **args)
    return dict(args=args, result=res, figures={"out": out},
                inputs=["上一件工具出的专题图 + 统计柱状图"],
                caption="一页式报告：地图 + 图表 + 关键数字",
                note="它是排版工具，不做分析；数字与图都要先前算好。")


@example("vis.bar_chart")
def ex_bar(F):
    mask = read_mask(F["mask_damage"])
    out = WORK / "bar.png"
    args = {"data": {"intact": int((mask == 1).sum()), "partial": int((mask == 2).sum()),
                     "destroyed": int((mask == 3).sum())},
            "output_path": str(out), "title": "Building Damage by Class"}
    res = run_tool(E("vis.bar_chart"), **args)
    return dict(args=args, result=res, figures={"out": out},
                inputs=["seg.building_damage 掩膜的逐类像元计数"],
                caption="按损毁等级统计的像元数（数据来自上一件工具的掩膜）",
                note="图表工具只负责画，不做统计；数据要自己先算好。")


@example("vis.line_chart")
def ex_line(F):
    out = WORK / "line.png"
    args = {"data": {"2021-07-18": 12.4, "2021-07-19": 28.9, "2021-07-20": 41.6,
                     "2021-07-21": 39.2, "2021-07-22": 33.0, "2021-07-23": 24.7},
            "output_path": str(out), "title": "Flooded Area over Time (km2)"}
    res = run_tool(E("vis.line_chart"), **args)
    return dict(args=args, result=res, figures={"out": out}, status="demo",
                inputs=["一组「日期 → 数值」点（示意数据，用于展示折线图能力）"],
                caption="折线图输出（数据为示意）",
                note="图表工具与数据来源无关；换成真实的逐日淹没面积即可直接出图。")


@example("vis.pie_chart")
def ex_pie(F):
    mask = read_mask(F["mask_damage"])
    out = WORK / "pie.png"
    args = {"data": {"intact": int((mask == 1).sum()), "partial": int((mask == 2).sum()),
                     "destroyed": int((mask == 3).sum())},
            "output_path": str(out), "title": "Damage Composition"}
    res = run_tool(E("vis.pie_chart"), **args)
    return dict(args=args, result=res, figures={"out": out},
                inputs=["损毁掩膜的逐类像元计数"],
                caption="占比饼图",
                note="类别多于 6 个时颜色会重复，建议先合并小类。")


@example("vis.heatmap")
def ex_heatmap(F):
    args = {"points_path": str(F["points"]), "base_image_path": str(F["tokyo"]),
            "bandwidth": 12, "colormap": "inferno"}
    res = run_tool(E("vis.heatmap"), **args)
    out = first_path(res)
    return dict(args=args, result=res, figures={"out": out} if out else {},
                inputs=["Tokyo OSM 点要素（EPSG:6677）", "同区域影像"],
                caption="点密度热力图（核密度）",
                note="带宽 `bandwidth` 决定平滑程度；点与底图必须同坐标系、同上限范围。")


@example("vis.add_map_elements")
def ex_add_elements(F):
    args = {"image_path": str(WORK / "damage_map.png"),
            "title": "Annotated Map", "legend_items": [{"label": "Destroyed", "color": [220, 40, 40]},
                              {"label": "Partial", "color": [255, 190, 40]}],
            "north_arrow": True, "scale_bar": True, "pixel_size_m": 0.8}
    if not (WORK / "damage_map.png").exists():
        ex_damage_map(F)
    res = run_tool(E("vis.add_map_elements"), **args)
    out = first_path(res)
    return dict(args=args, result=res, figures={"out": out} if out else {},
                inputs=["上一件工具出的专题图"],
                caption="给已有图片补图例、指北针、比例尺",
                note="用于美化外部图片；自己出图直接用 `vis.damage_map` 更省事。")


@example("ras.area")
def ex_area(F):
    args = {"mask_path": str(F["mask_landslide"]), "pixel_size_m": 10.0, "classes": [1]}
    res = run_tool(E("ras.area"), **args)
    return dict(args=args, result=res, figures={},
                inputs=["滑坡掩膜（10 m 分辨率整景）"],
                caption="", note="面积 = 像元数 × 10 m × 10 m，不含模型误差修正。")


@example("ras.stats")
def ex_stats(F):
    args = {"image_path": str(F["geo"]), "band": 4}
    res = run_tool(E("ras.stats"), **args)
    return dict(args=args, result=res, figures={},
                inputs=["Japan_all_14_sentinel.tif 第 4 波段"],
                caption="", note="单波段统计，整幅一次约 1 秒，不走模型。")


@example("ras.count_pixels")
def ex_count(F):
    args = {"mask_path": str(F["mask_damage"]), "classes": [2, 3]}
    res = run_tool(E("ras.count_pixels"), **args)
    return dict(args=args, result=res, figures={},
                inputs=["损毁掩膜（类别 1/2/3）"],
                caption="", note="只数像元，不做面积换算；要面积用 `ras.area`。")


@example("ras.threshold")
def ex_threshold(F):
    args = {"image_path": str(F["geo"]), "threshold": 1200.0, "op": ">", "band": 7}
    res = run_tool(E("ras.threshold"), **args)
    path = next((res[k] for k in res if k.endswith("_path") and res[k]), None)
    fig = {}
    if path:
        m = read_mask(path)
        img = to_rgb(read_bands(F["geo"]), (2, 1, 0))
        fig["out"] = three_panel(img, (m > 0).astype(np.uint8) * 255, LANDSLIDE)
    return dict(args=args, result=res, figures=fig,
                inputs=["Japan_all_14_sentinel.tif 第 7 波段（近红外）"],
                caption="影像｜阈值掩膜｜叠加（亮像元 > 1200）",
                note="阈值法零成本、可解释，但没有语义；找水体/裸土够用，找「滑坡」不行。")


@example("mask.compose_multiclass")
def ex_compose(F):
    args = {"mask_paths": [str(F["mask_c2"]), str(F["mask_c3"])], "class_values": [2, 3]}
    res = run_tool(E("mask.compose_multiclass"), **args)
    path = next((res[k] for k in res if k.endswith("_path") and res[k]), None)
    fig = {}
    if path:
        img = to_rgb(read_bands(F["rgb"]), (0, 1, 2), ref=50)
        fig["out"] = three_panel(img, read_mask(path), DAMAGE)
    return dict(args=args, result=res, figures=fig,
                inputs=["类别 2、3 各自的二值掩膜（由损毁掩膜拆出）"],
                caption="两张二值掩膜合成一张多类掩膜",
                note="多模型各自只出二值时用它合并；类别值要预先约定好，别两处不一致。")


@example("poi.group_by")
def ex_group(F):
    gj = json.loads(F["poi"].read_text(encoding="utf-8"))
    rows = [f["properties"] for f in gj["features"] if f.get("properties")]
    field = "fclass" if "fclass" in rows[0] else sorted(rows[0])[0]
    args = {"data": rows, "group_field": field}
    res = run_tool(E("poi.group_by"), **args)
    return dict(args=args, result=res, figures={},
                inputs=["noto 地震 POI 属性表（307 条）"],
                caption="", note="按设施类型统计数量；属性直接来自 GeoJSON，不是造的。")


@example("poi.to_vector")
def ex_poi_vector(F):
    args = {"geojson_path": str(F["poi"]), "name": "hospital", "exact": False}
    res = run_tool(E("poi.to_vector"), **args)
    return dict(args=args, result=res, figures={},
                inputs=["noto 地震 POI（307 个点）"],
                caption="", note="按名称筛点并落成新的 GeoJSON；名称匹配是大小写无关的子串匹配。")


@example("poi.search_by_name")
def ex_poi_search(F):
    args = {"geojson_path": str(F["poi"]), "name": "school", "exact": False}
    res = run_tool(E("poi.search_by_name"), **args)
    return dict(args=args, result=res, figures={},
                inputs=["noto 地震 POI"],
                caption="", note="只返回匹配到的点与属性，不落盘。")


@example("poi.world_to_pixel")
def ex_poi_pixel(F):
    args = {"geojson_path": str(F["points_clean"]), "raster_path": str(F["tokyo"])}
    res = run_tool(E("poi.world_to_pixel"), **args)
    return dict(args=args, result=res, figures={},
                inputs=["Tokyo OSM 点要素（EPSG:4326）", "同区域影像 image_opt.tif（EPSG:6677）"],
                caption="", note="**输入 GeoJSON 必须是经纬度**：工具内部固定按 EPSG:4326 解释再转成栅格坐标系，"
                     "喂投影坐标会算出图外的行列号。")


@example("poi.damage_population_exposure")
def ex_exposure(F):
    dmg = [{"name": "block_a", "max": 3}, {"name": "block_b", "max": 2}, {"name": "block_c", "max": 1}]
    pop = [{"name": "block_a", "max": 1200}, {"name": "block_b", "max": 800}, {"name": "block_c", "max": 450}]
    args = {"damage_feature_stats": dmg, "population_feature_stats": pop, "damage_threshold": 2.0}
    res = run_tool(E("poi.damage_population_exposure"), **args)
    return dict(args=args, result=res, figures={}, status="demo",
                inputs=["两个按 name 对齐的属性表（示意数据，结构同 `poi.group_by` 的输出）"],
                caption="", note="按 name 做连接，统计受损格网里的人口；真实使用时两个表来自同一套格网。")


@example("model.summarize")
def ex_summarize(F):
    args = {"task_question": "Which district has the most destroyed buildings?",
            "trajectory": [{"tool": "seg.building_damage", "arguments": {"post_image_path": "post.png"},
                            "result": {"mask_path": "mask.png"}},
                           {"tool": "vis.damage_map", "arguments": {"base_image_path": "post.png"}}],
            "image_paths": [], "model": "gpt-4o-mini"}
    res = {
        "tool": "model.summarize",
        "model": "gpt-4o-mini",
        "summary": "Building damage concentrates in the north-western block: 2,073 pixels were classified "
                   "as totally destroyed and 25,880 as partially damaged, i.e. partial damage dominates.",
        "backend": "gpt",
        "_example": {"wall_time_s": None},
    }
    return dict(args=args, result=res, figures={}, status="constructed",
                inputs=["一个 2 步的轨迹 + 问题文本（示意）"],
                caption="",
                note="**构造示意**：本机没有 GPT key，这段返回按源码的字段结构手写，未实际调用。"
                     "真实使用时它会读轨迹里的工具结果与图片，生成一段自然语言结论。")


@example("report.extract_evidence")
def ex_evidence(F):
    traj = [{"tool": "seg.building_damage", "arguments": {"post_image_path": "post.png"},
             "result": {"mask_path": str(F["mask_damage"])}},
            {"tool": "ras.area", "arguments": {"mask_path": "m.tif", "pixel_size_m": 0.8},
             "result": {"area_m2": 16562.0}}]
    args = {"trajectory": traj, "pixel_size_m": 0.8, "include_empty_masks": False,
            "target_classes": [1, 2, 3]}
    res = run_tool(E("report.extract_evidence"), **args)
    return dict(args=args, result=res, figures={}, status="demo",
                inputs=["一段含掩膜产物的轨迹（示意轨迹 + 真实掩膜文件）"],
                caption="", note="它把轨迹里的掩膜折算成面积与类别统计，是「把过程变成证据」的一步。")


@example("tool.loop")
def ex_loop(F):
    args = {"calls": [{"tool": "ras.area",
                        "args": {"mask_path": str(F["mask_landslide"]), "pixel_size_m": 10.0}}],
            "loop_over": [{"scene": "japan"}, {"scene": "japan"}],
            "return_all": False, "show_progress": False}
    res = run_tool(E("tool.loop"), **args)
    return dict(args=args, result=res, figures={}, status="demo",
                inputs=["同一件工具、两组参数（示意，演示批量调用）"],
                caption="", note="把「同一工具换参数跑多次」收成一次调用；返回里含每次的结果与汇总。")


@example("vec.graph_shortest_path")
def ex_shortest(F):
    start, end = graph_endpoints(F)
    args = {"graph_path": str(F["graph"]), "start": start, "end": end, "pixel_size_m": 0.2}
    res = run_tool(E("vec.graph_shortest_path"), **args)
    img = to_rgb(read_bands(F["tokyo"]), (0, 1, 2), ref=55)
    return dict(args=args, result=res,
                figures={"out": draw_polygons(img, F["roads"], None)} if False else {},
                inputs=["vec.build_graph 生成的路网图（Tokyo OSM 道路）"],
                caption="", note="起点终点是像素坐标；图与影像必须同坐标系。")


@example("vec.build_graph")
def ex_build_graph(F):
    args = {"centerline_path": str(F["roads_single"])}
    res = run_tool(E("vec.build_graph"), **args)
    img = to_rgb(read_bands(F["tokyo"]), (0, 1, 2), ref=55)
    return dict(args=args, result=res,
                figures={"out": draw_polygons(img, F["roads"], None)},
                inputs=["Tokyo OSM 道路中心线（193 条，EPSG:6677，已炸成单部件）"],
                caption="建图用的路网（红线为参与建图的中心线）",
                note="**MultiLineString 会直接报错**（`Sub-geometries may have coordinate sequences`），"
                     "建图前要先 `explode` 成单部件。")


@example("vec.voronoi")
def ex_voronoi(F):
    args = {"points_path": str(F["points"]), "boundary_path": str(F["buildings"])}
    res = run_tool(E("vec.voronoi"), **args)
    path = next((res[k] for k in res if k.endswith("_path") and res[k]), None)
    fig = {}
    if path:
        fig["out"] = draw_polygons(colorize(np.zeros((600, 800), np.uint8), {}) + 245, path, None)
    return dict(args=args, result=res, figures=fig,
                inputs=["Tokyo OSM 点要素 + 用作边界的建筑面"],
                caption="泰森多边形（每个点的影响范围）",
                note="边界决定裁剪范围；点太少时多边形会很大，注意配合边界使用。")


@example("seg.vegetation")
def ex_vegetation(F):
    args = {"image_path": str(F["rgb"])}
    res = run_tool(E("seg.vegetation"), **args)
    mask = read_mask(res["mask_path"])
    img = to_rgb(read_bands(F["rgb"]), (0, 1, 2), ref=50)
    return dict(args=args, result=res,
                figures={"in": img, "out": three_panel(img, (mask > 0).astype(np.uint8) * 255, VEG)},
                inputs=["xbd 灾后影像（3 波段，0–255）"],
                caption="影像｜植被掩膜｜叠加（文档说输出 5/6 类，实际是 0/255）",
                note="**文档与实现不一致**：工具返回 `classes: {5, 6}`，实际掩膜只有 0 和 255；统计请按 `>0`。")


@example("seg.reservoir")
def ex_reservoir(F):
    args = {"post_image_path": str(F["geo14"])}
    res = run_tool(E("seg.reservoir"), **args)
    mask = read_mask(res["mask_path"])
    img = to_rgb(read_bands(F["geo14"]), (2, 1, 0))
    return dict(args=args, result=res,
                figures={"in": img, "out": three_panel(img, mask, WATER)},
                inputs=["14 波段日本山区影像（ras.concat 产物）——本例场景里没有水库，只看接口"],
                caption="影像｜水库水面｜叠加",
                note="只出水面范围；库容要靠「水面面积 × 水位—面积曲线」另外算。")


@example("seg.building_lowres")
def ex_lowres(F):
    args = {"image_path": str(F["rgb"])}
    res = run_tool(E("seg.building_lowres"), **args)
    mask = read_mask(res["mask_path"])
    img = to_rgb(read_bands(F["rgb"]), (0, 1, 2), ref=50)
    return dict(args=args, result=res,
                figures={"in": img, "out": three_panel(img, mask, DAMAGE)},
                inputs=["xbd 灾后影像（1024²，0.8 m）"],
                caption="影像｜低分辨率建筑模型输出｜叠加",
                note="为 480 px 窗口设计，512² 就要 5.5 GB 内存；大图请先切块。")


@example("seg.water_aerial")
def ex_water_aerial(F):
    args = {"post_image_path": str(F["aerial"])}
    res = run_tool(E("seg.water_aerial"), **args)
    mask = read_mask(res["mask_path"])
    img = to_rgb(read_bands(F["aerial"]), (0, 1, 2), ref=55)
    return dict(args=args, result=res,
                figures={"in": img, "out": three_panel(img, mask, WATER)},
                inputs=["mayfield 无人机影像 0.03 m（裁 1024²）"],
                caption="影像｜航拍水体｜叠加",
                note="只认 0.03 m 无人机视角；喂卫星影像（0.5 m 以上）会大面积误判。")


@example("seg.building_damage_opt_sar")
def ex_opt_sar(F):
    args = {"pre_image_path": str(F["flood_pre"]), "post_image_path": str(F["flood_sar"])}
    res = run_tool(E("seg.building_damage_opt_sar"), **args)
    mask = read_mask(res["mask_path"])
    img = to_rgb(read_bands(F["flood_pre"]), (0, 1, 2), ref=55)
    return dict(args=args, result=res,
                figures={"out": three_panel(img, mask, DAMAGE)},
                inputs=["libya 灾前光学 + 灾后 SAR（VV）"],
                caption="灾前光学｜SAR 后判出的损毁｜叠加",
                note="SAR 侧需要先做辐射定标与地理编码；工具里没有这些预处理，直接喂原始 SLC 不行。",
                status="demo")


# ---------------------------------------------------------------- 自动配方（纯算法类）


FIXTURE_DESC = {
    "rgb": "xbd guatemala_volcano_00000004 灾后影像（0.8 m，1024²，RGB）",
    "rgb_pre": "同地点灾前影像",
    "flood": "libya_flood_post_4_8.png（德尔纳洪灾，灾后）",
    "flood_pre": "libya_flood_pre_4_8.png（灾前）",
    "geo": "images/landslide4sense/Japan_all_14_sentinel.tif（12 波段，EPSG:4326）",
    "geo14": "ras.concat 拼出的 14 波段日本山区影像",
    "dem": "images/landslide4sense/Japan_all_14_dem.tif（高程，米）",
    "mask_damage": "seg.building_damage 输出的损毁掩膜（类别 1/2/3）",
    "mask_landslide": "seg.landslide_ms 输出的滑坡掩膜（0/1）",
    "mask_c2": "损毁掩膜中的「部分损毁」二值掩膜",
    "mask_c3": "损毁掩膜中的「完全损毁」二值掩膜",
    "buildings": "images/heatisland/09LD1638/osm/buildings.geojson（79 个建筑面，已转 EPSG:6677）",
    "landuse": "同目录 landuse.geojson（已转 EPSG:6677）",
    "roads": "同目录 roads.geojson（193 条道路，已转 EPSG:6677）",
    "roads_single": "roads.geojson 炸成单部件后的版本（build_graph 不支持 MultiLineString）",
    "points": "同目录 points.geojson（OSM 点要素，已转 EPSG:6677）",
    "points_in": "points.geojson 裁到影像范围内的子集（world_to_pixel 要求点在图内）",
    "graph": "vec.build_graph 生成的路网图（JSON）",
    "tokyo": "images/heatisland/09LD1638/image_opt.tif（EPSG:6677）",
    "poi": "images/disasterm3/noto_earthquake_agent2/…_poi.geojson（307 个点）",
    "poi_utm": "mayfield region_01 POI（已转 EPSG:32616）",
    "aerial": "mayfield region_01 无人机影像 0.03 m（裁 1024²）",
    "roi": "覆盖 buildings 西半幅的矩形，用作裁剪范围",
    "roads_buffer": "roads 外扩 30 m 的缓冲区，用于演示矢量求交",
}

OVERRIDES: dict[str, dict[str, str]] = {
    "vec.length": {"vector_path": "roads"},
    "vec.kbuffer": {"vector_path": "roads"},
    "vec.clip": {"vector_path": "buildings", "roi_vector_path": "roi"},
    "vec.intersect": {"vector_a_path": "buildings", "vector_b_path": "roads_buffer"},
    "vec.nearest": {"vector_a_path": "buildings", "vector_b_path": "points"},
    "vec.point_in_polygon": {"points_path": "points_in", "polygons_path": "buildings"},
    "vec.raster_stats": {"vector_path": "buildings", "raster_path": "tokyo"},
    "vec.pixel_to_world": {"raster_path": "tokyo"},
    "vec.filter_by_distance": {"vector_path": "buildings"},
    "vec.dissolve": {"vector_path": "buildings"},
    "vec.simplify": {"vector_path": "buildings"},
    "vec.convex_hull": {"vector_path": "buildings"},
    "vec.max_polygon": {"vector_path": "buildings"},
    "vec.perimeter": {"vector_path": "buildings"},
    "vec.centroid": {"vector_path": "buildings"},
    "vec.connected_components": {"vector_path": "buildings"},
    "vec.filter_by_area": {"vector_path": "buildings"},
    "vec.filter_by_attribute": {"vector_path": "buildings"},
    "vec.buffer": {"vector_path": "buildings"},
    "ras.diff": {"image_a_path": "geo", "image_b_path": "geo"},
    "ras.focal_stats": {"raster_path": "geo"},
    "ras.resample": {"raster_path": "geo"},
    "ras.sample_point": {"image_path": "geo"},
    "ras.sample_points": {"image_path": "geo"},
    "ras.grid_windows": {"image_path": "geo"},
    "seg.bridge": {"post_image_path": "rgb"},
    "seg.storage_tank": {"post_image_path": "rgb"},
    "seg.harbor": {"post_image_path": "rgb"},
    "seg.plane": {"post_image_path": "rgb"},
    "seg.vehicle": {"post_image_path": "rgb"},
    "seg.playground": {"post_image_path": "rgb"},
    "seg.roundabout": {"post_image_path": "rgb"},
    "seg.ship": {"post_image_path": "rgb"},
    "seg.swimming_pool": {"post_image_path": "rgb"},
    "seg.pool_aerial": {"post_image_path": "aerial"},
    "seg.lava": {"pre_image_path": "volcano_a", "post_image_path": "volcano_b"},
    "ras.threshold": {"image_path": "geo"},
}

AUTO_MAP: dict[str, tuple[str, str]] = {
    "image_path": ("rgb", "path"),
    "post_image_path": ("rgb", "path"),
    "pre_image_path": ("rgb_pre", "path"),
    "base_image_path": ("rgb", "path"),
    "mask_path": ("mask_damage", "path"),
    "raster_path": ("geo", "path"),
    "dem_path": ("dem", "path"),
    "vector_path": ("buildings", "path"),
    "vector_a_path": ("buildings", "path"),
    "vector_b_path": ("landuse", "path"),
    "roi_vector_path": ("buildings", "path"),
    "points_path": ("points", "path"),
    "polygons_path": ("buildings", "path"),
    "centerline_path": ("roads", "path"),
    "graph_path": ("graph", "path"),
    "geojson_path": ("poi", "path"),
    "image_paths": (["rgb", "rgb_pre"], "list"),
    "image_path_list": (["geo", "geo_slope", "dem"], "list"),
    "mask_paths": (["mask_c2", "mask_c3"], "list"),
}

SCALARS = {
    "a": 1.0, "b": 2.0, "pixel_size_m": 0.8, "threshold": 0.5, "meter": 20.0,
    "meters": [20.0, 40.0], "tolerance": 0.0001, "min_area_m2": 20.0,
    "values": [3.0, 4.0, 5.0], "weights": [0.5, 0.3, 0.2], "normalize": True,
    "area_m2": 12000.0, "depth_m": 0.8, "volume_m3": 8000.0, "capacity_m3": 12.0,
    "point_a": [0.0, 0.0], "point_b": [30.0, 40.0],
    "row": 512, "col": 512,
    "points": [{"row": 100, "col": 120}, {"row": 300, "col": 400}],
    "classes": [2, 3], "class_values": [2, 3], "intact_classes": [1],
    "damaged_classes": [2, 3], "band": 1, "statistic": "mean", "window_size": 5,
    "target_pixel_size_m": 20.0, "resampling": "nearest", "dst_crs": "EPSG:32654",
    "x1": 100, "x2": 600, "y1": 100, "y2": 600, "n": 4,
    "pixel_row": 200, "pixel_col": 300, "azimuth": 315, "altitude": 45, "z_factor": 1.0,
    "start": [40, 40], "end": [900, 1200], "source": "a", "target": "b",
    "center_lat": 35.69, "center_lon": 139.70, "max_distance_m": 800.0,
    "start_point": [10, 10], "end_point": [200, 300],
    "damage_threshold": 2.0, "min_damage_class": 2, "exact": False,
    "attribute_name": "type", "allowed_values": ["residential"],
    "polygon_id_field": "osm_id", "stats": "mean", "min_pixels": 1,
    "all_touched": False, "return_features": False, "by": "type",
    "name": "school", "total_supply": 1000.0, "min_per_site": 50.0,
    "items": [{"name": "A", "score": 0.9}, {"name": "B", "score": 0.6}],
    "criteria": {"score": 1.0}, "top_k": 3, "values_field": "score",
    "field": "score", "mode": "sum", "sort_by": "value", "descending": True,
    "round_digits": 2, "label_field": "name", "value_field": "score",
    "trajectory": [], "include_empty_masks": False, "target_classes": [1, 2, 3],
    "legend_items": {"Damaged": "#FF6600"}, "legend_alpha": 0.85,
    "point_markers": True, "north_arrow": True, "scale_bar": True,
    "bandwidth": 12, "colormap": "inferno", "alpha": 0.45,
    "class_labels": {"1": "Intact", "2": "Partial", "3": "Destroyed"},
    "summary_text": "", "key_statistics": {}, "columns": 3, "labels": [],
    "path_pixels": [[10, 10], [100, 100], [200, 300]], "route_color": [255, 0, 0],
    "route_width": 4, "grid_n": 4, "return_all": False, "show_progress": False,
    "bind": {}, "loop_over": [], "calls": [], "demands": [],
    "snap_buffer_px": 3, "blocked_attr": "blocked", "preserve_topology": True,
    "ignore_nodata": True, "nodata": None, "dim": "bands", "op": ">",
    "true_value": 255, "false_value": 0, "band_a": 1, "band_b": 1,
}


def auto_recipe(tool: str):
    t = TOOLS[tool]

    def run(F):
        args: dict = {}
        used: list[str] = []
        ov = OVERRIDES.get(tool, {})
        for p in t["params"]:
            if not p["required"]:
                continue
            name = p["name"]
            if name in ov:
                args[name] = str(F[ov[name]])
                used.append(ov[name])
            elif name == "data":
                gj = json.loads(F["poi"].read_text(encoding="utf-8"))
                args[name] = [f["properties"] for f in gj["features"] if f.get("properties")]
                used.append("poi")
            elif name in AUTO_MAP:
                key, kind = AUTO_MAP[name]
                if kind == "list":
                    args[name] = [str(F[k]) for k in key]
                    used.extend(key)
                else:
                    args[name] = str(F[key])
                    used.append(key)
            elif name in SCALARS:
                args[name] = SCALARS[name]
            else:
                raise KeyError(f"{tool}: 参数 {name} 没有映射")
        mod = importlib.import_module(f"dora.tools.{t['module']}")
        fn = getattr(mod, t["func"])
        res = run_tool(fn, **args)

        fig = {}
        img_key = next((k for k in ("image_path", "base_image_path", "post_image_path") if k in args), None)
        base = None
        if img_key:
            base = to_rgb(read_bands(args[img_key]), (0, 1, 2), ref=55)
            fig["in"] = base
        for k, v in res.items():
            if not isinstance(v, str) or not k.endswith("_path") or not Path(v).exists():
                continue
            if v.endswith(".geojson"):
                # 没有输入影像时，用同坐标系的 Tokyo 影像当底图，矢量才看得见
                if base is None:
                    base = to_rgb(read_bands(F["tokyo"]), (0, 1, 2), ref=55)
                    fig["in"] = base
                    with rasterio.open(F["tokyo"]) as src:
                        tr = src.transform
                    fig["out"] = draw_polygons(base, v, tr)
                else:
                    fig["out"] = draw_polygons(base, v, None)
                continue
            if v.endswith((".tif", ".png", ".jpg")):
                arr = read_bands(v)
                if arr.shape[0] == 1 and base is not None and arr.shape[1:] == base.shape[:2]:
                    uniq = np.unique(arr[0])
                    colors = DAMAGE if (len(uniq) <= 8 and set(uniq.astype(int)) <= {0, 1, 2, 3}) else LANDSLIDE
                    fig["out"] = three_panel(base, arr[0].astype(np.uint8), colors)
                else:
                    fig["out"] = render_raster(v)
                break
        inputs = [FIXTURE_DESC[u] for u in dict.fromkeys(used) if u in FIXTURE_DESC]
        caption = ""
        if fig.get("out") is not None and base is not None and fig.get("in") is not None:
            caption = "上：输入影像；下：影像｜掩膜｜叠加" if fig["out"].shape == fig["in"].shape                 else "上：输入影像；下：处理结果"
        elif fig.get("out") is not None:
            caption = "处理结果"
        return dict(args=args, result=res, figures=fig, inputs=inputs, caption=caption,
                    note="", status="real")

    return run


# ---------------------------------------------------------------- 主流程


def domain_dir(tool: str) -> str:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import content  # noqa: PLC0415

    return dict(content.DOMAINS)[TOOLS[tool]["domain"]]


def main(argv: list[str]) -> int:
    F = fixtures()

    for name in TOOLS:
        if name not in EXAMPLES:
            EXAMPLES[name] = {"fn": auto_recipe(name), "status": "real"}

    targets = [a for a in argv if not a.startswith("-")] or list(TOOLS)
    ok, fail = 0, []
    for tool in targets:
        spec = EXAMPLES.get(tool)
        if not spec:
            print(f"[skip] {tool} 未登记")
            continue
        print(f"[run ] {tool}", flush=True)
        try:
            data = spec["fn"](F)
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            fail.append((tool, str(exc)))
            continue

        folder = EX / domain_dir(tool) / tool
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "input.json").write_text(
            json.dumps(sanitize(data["args"]), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n")
        payload = dict(data["result"])
        payload.pop("_example", None)
        (folder / "output.json").write_text(
            json.dumps(sanitize(trim(payload)), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n")
        figs = {}
        for key, val in (data.get("figures") or {}).items():
            if val is None:
                continue
            dst = folder / f"{key}.webp"
            save_webp(val if isinstance(val, np.ndarray) else Image.open(val), dst)
            figs[key] = dst.name
        (folder / "meta.json").write_text(json.dumps({
            "tool": tool,
            "inputs": data.get("inputs", []),
            "figures": figs,
            "caption": data.get("caption", ""),
            "note": data.get("note", ""),
            "status": data.get("status", spec.get("status", "real")),
            "wall_time_s": (data.get("result") or {}).get("_example", {}).get("wall_time_s"),
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        ok += 1
        print(f"[ok  ] {tool} -> {folder.relative_to(REPO)}")

    print(f"\n完成 {ok} 件，失败 {len(fail)} 件")
    for tool, err in fail:
        print(f"  - {tool}: {err[:160]}")
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main(_ARGV))
