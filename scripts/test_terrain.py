"""Self-test for the extended terrain tools, on synthetic DEMs with a known answer.

    uv run --no-project --python <venv>/python.exe scripts/test_terrain.py

Every case has an analytically known result, so a failure means the implementation is wrong,
not that the tolerance is too tight.
"""
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from skimage import measure

REPO = Path(__file__).resolve().parents[1]
TMP = Path(tempfile.mkdtemp(prefix="terrain_test_"))
sys.argv = [sys.argv[0], "--temp_dir", str(TMP)]          # what the MCP servers get
sys.path.insert(0, str(REPO / "src"))

from dora.tools import terrain as T  # noqa: E402

CELL = 10.0
N = 64
ok, failed = 0, 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global ok, failed
    if cond:
        ok += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {detail}")


def write_dem(name: str, z: np.ndarray) -> str:
    p = TMP / f"{name}.tif"
    prof = {"driver": "GTiff", "height": z.shape[0], "width": z.shape[1], "count": 1,
            "dtype": "float32", "crs": "EPSG:32654",
            "transform": from_origin(500000, 4000000, CELL, CELL)}
    with rasterio.open(p, "w", **prof) as dst:
        dst.write(z.astype(np.float32), 1)
    return str(p)


def load(res: str, key: str = "") -> dict:
    d = json.loads(res)
    assert "error" not in d, d
    return d


print("\n[1] 平面：z = 0.1 * x（向东升高 10%）→ 坡度 5.71°，坡向 270°（向西下坡）")
x = np.arange(N) * CELL
plane = np.tile(x * 0.1, (N, 1))
d = load(T.ras_terrain(write_dem("plane", plane), attributes="slope,aspect"),
         "paths")
with rasterio.open(d["paths"]["slope"]) as s:
    pslope = s.read(1)
with rasterio.open(d["paths"]["aspect"]) as s:
    asp = s.read(1)
# 边缘一列按复制填充，梯度被削半，这是卷积类算法的正常边界效应；比较内部
check("坡度中位数 5.71°", abs(float(np.median(pslope[2:-2, 2:-2])) - math.degrees(math.atan(0.1))) < 0.01,
      f"得到 {np.median(pslope[2:-2, 2:-2]):.3f}")
check("坡向均值 270°", abs(float(np.nanmean(asp[2:-2, 2:-2])) - 270) < 0.5,
      f"得到 {np.nanmean(asp[2:-2, 2:-2]):.2f}")

print("\n[2] 平地：所有地形属性应为 0（TRI/TPI/粗糙度/曲率在内部无起伏）")
flat = np.full((N, N), 100.0)
d = load(T.ras_terrain(write_dem("flat", flat)), "paths")
for name in ("tri", "tpi", "roughness"):
    with rasterio.open(d["paths"][name]) as s:
        arr = s.read(1)
    check(f"{name} 全 0", float(np.nanmax(np.abs(arr))) < 1e-4, f"max|{name}|={np.nanmax(np.abs(arr)):.3g}")

print("\n[3] 圆锥：山顶 TPI 为正、TRI 大于 0、曲率为正（凸地形）")
yy, xx = np.mgrid[0:N, 0:N]
r = np.hypot(yy - N / 2, xx - N / 2) * CELL
cone = 200 - r
d = load(T.ras_terrain(write_dem("cone", cone), attributes="tpi,tri,curvature,slope"), "paths")
with rasterio.open(d["paths"]["tpi"]) as s:
    tpi = s.read(1)
with rasterio.open(d["paths"]["curvature"]) as s:
    curv = s.read(1)
with rasterio.open(d["paths"]["slope"]) as s:
    cslope = s.read(1)
check("山顶 TPI > 0", tpi[N // 2, N // 2] > 0, f"tpi={tpi[N // 2, N // 2]:.2f}")
check("山顶曲率 > 0", curv[N // 2, N // 2] > 0, f"curv={curv[N // 2, N // 2]:.3f}")
check("圆锥坡度恒为 45°（内部）", abs(float(np.median(cslope[5:-5, 5:-5])) - 45) < 1.5,
      f"median={np.median(cslope[5:-5, 5:-5]):.2f}")

print("\n[4] 流向：整体向南倾斜 → D8 全为 4（南），汇流最大值 ≈ 行数×列数 的路径长度")
south = np.tile((N - np.arange(N))[:, None] * 1.0, (1, N))
d = load(T.ras_flow(write_dem("south", south)), "paths")
with rasterio.open(d["paths"]["flow_direction"]) as s:
    fdir = s.read(1)
with rasterio.open(d["paths"]["flow_accumulation"]) as s:
    facc = s.read(1)
check("内部流向全为 4（南）", set(np.unique(fdir[1:-1, 1:-1]).tolist()) == {4},
      f"unique={np.unique(fdir[1:-1, 1:-1])[:6]}")
check("无洼地（filled_cells=0）", d["stats"]["filled_cells"] == 0, str(d["stats"]))
# 整体向南倾斜时，每一列的水都汇到底边，底行每格汇流量 = 列长
check("底行汇流 = 64（列长）", abs(d["stats"]["max_accumulation"] - N) < 1e-6,
      f"max={d['stats']['max_accumulation']}")

print("\n[5] 洼地：中间挖一个坑，填洼后坑内应能排出，且填平方数 > 0")
bowl = np.full((N, N), 100.0)
bowl[20:40, 20:40] = 90.0                        # 20x20 的坑，四周边界仍为 100
bowl[0, 32] = 99.0                               # 北边界开一个口
d = load(T.ras_flow(write_dem("bowl", bowl)), "paths")
check("填洼抬高了坑内像元", d["stats"]["filled_cells"] >= 300, str(d["stats"]))
with rasterio.open(d["paths"]["flow_direction"]) as s:
    bdir = s.read(1)
# 填洼的目的就是让洼地内部每一格都有去路；边界格为 0 是正常的（水流出图幅）
check("填洼后内部无死水格", int((bdir[1:-1, 1:-1] == 0).sum()) == 0,
      f"{(bdir[1:-1, 1:-1] == 0).sum()} 个内部格无出口")
with rasterio.open(d["paths"]["flow_accumulation"]) as s:
    bacc = s.read(1)
check("坑内存在汇流累积（水能汇集并流出）", bacc[20:40, 20:40].max() > 5,
      f"max={bacc[20:40, 20:40].max()}")

print("\n[6] 等高线：斜坡 z = 0.5x/像元，高程 0–315 m，间隔 50 m → 6 条等值线、每级一条直线")
ramp = np.tile(np.arange(N) * CELL * 0.5, (N, 1))
res = load(T.ras_contour(write_dem("ramp", ramp), interval=50.0), "out_path")
check("等值线数量 6", res["n_lines"] == 6, f"得到 {res['n_lines']}，levels={res['levels']}")
check("高程为 50/100/…/300", res["levels"] == [50.0, 100.0, 150.0, 200.0, 250.0, 300.0],
      str(res["levels"]))
check("总长度 > 0", res["total_length_m"] > 0, str(res["total_length_m"]))
gj = json.loads(Path(res["out_path"]).read_text(encoding="utf-8"))
check("GeoJSON 是 LineString 集合", gj["type"] == "FeatureCollection"
      and all(f["geometry"]["type"] == "LineString" for f in gj["features"]))
check("每条线带高程属性", all("elevation" in f["properties"] for f in gj["features"]))

print("\n[7] 流域：V 形谷（沿行缓降 0.1 m/行，向中列收拢 0.5 m/列）→ 底边中央出口应圈住全图")
r_, c_ = np.mgrid[0:N, 0:N]
vv = (N - r_) * 0.1 + np.abs(c_ - 32) * 0.5
vp = write_dem("vvalley", vv)


def wpt(c: int, r: int) -> tuple[float, float]:
    """像元 (row=r, col=c) 的世界坐标中心，方便按「第几行第几列」写测试。"""
    return 500000 + (c + 0.5) * CELL, 4000000 - (r + 0.5) * CELL


def cc(tag: str, *args, **kw) -> dict:
    """每次调用写到独立 out_dir：流域的产物文件名固定，共用目录会互相覆盖。"""
    kw["out_dir"] = str(TMP / f"c_{tag}")
    return load(T.ras_catchment(vp, *args, **kw))


dc = cc("one", "%s,%s" % wpt(32, 63))
o1 = dc["outlets"][0]
check("单出口圈住全部 4096 格", o1["cells"] == N * N, f"cells={o1['cells']}")
check("面积 = 4096 × 100 m² = 0.4096 km²", abs(o1["area_km2"] - 0.4096) < 1e-4, str(o1["area_km2"]))
check("出口落在底边中央 (63, 32)", o1["pixel"] == [63, 32], str(o1["pixel"]))
tr7 = dc["truncation"]
check("四边计数之和 = border_cells（角落不重复算）",
      sum(tr7["by_side"].values()) == tr7["border_cells"],
      f"{tr7['by_side']} 之和 ≠ {tr7['border_cells']}")
check("回报出口在图幅边界", tr7["outlet_on_border"] is True)
check("只有 1 处水流出图", tr7["exits_on_border"] == 1, str(tr7["exits_on_border"]))

print("\n[8] 多出口：上游点 + 下游点 → 互斥分区，面积相加 = 全图，栅格无重叠")
dm = cc("two", "%s,%s;%s,%s" % (wpt(32, 32) + wpt(32, 63)))
p1, p2 = dm["outlets"]
check("两出口面积相加 = 4096", p1["cells"] + p2["cells"] == N * N,
      f"{p1['cells']} + {p2['cells']}")
check("上游点的流域只到它自己那一行", p1["cells"] == 33 * N, str(p1["cells"]))
with rasterio.open(dm["paths"]["catchment"]) as s:
    lab = s.read(1)
check("标签栅格只含 1、2", set(np.unique(lab).tolist()) == {1, 2}, str(np.unique(lab)))
check("两分区没有重叠格", int(((lab == 1) & (lab == 2)).sum()) == 0)

print("\n[9] 三种坐标给法（同 CRS 的 x,y / 像素 col,row / WGS84 经纬度）落到同一格")
x63, y63 = wpt(32, 63)
from pyproj import Transformer  # noqa: E402

lon, lat = Transformer.from_crs("EPSG:32654", "EPSG:4326", always_xy=True).transform(x63, y63)
pa = cc("same", f"{x63},{y63}", pour_crs="same")["outlets"][0]["pixel"]
pb = cc("pixel", "32,63", pour_crs="pixel")["outlets"][0]["pixel"]
pc = cc("wgs84", f"{lon},{lat}", pour_crs="wgs84")["outlets"][0]["pixel"]
check("same / pixel / wgs84 → (63, 32)", pa == pb == pc == [63, 32], f"{pa} {pb} {pc}")

print("\n[10] 不出水口的两种用法：省略点位（自动取边界最低格）与 snap 吸附")
da = cc("auto")
check("省略点位时自动选底边最低格", da["outlets"][0]["pixel"] == [63, 32], str(da["outlets"][0]["pixel"]))
d0 = cc("noseep", "%s,%s" % wpt(10, 10))
d1 = cc("snap", "%s,%s" % wpt(10, 10), snap_radius_m=300)
check("坡面中段不吸附：只圈到本列上游 11 格", d0["outlets"][0]["cells"] == 11, str(d0["outlets"][0]["cells"]))
check("吸附后面积变大", d1["outlets"][0]["cells"] > d0["outlets"][0]["cells"],
      f"{d0['outlets'][0]['cells']} → {d1['outlets'][0]['cells']}")
check("吸附距离不超过给定半径", d1["outlets"][0]["snap_distance_m"] <= 300,
      str(d1["outlets"][0]["snap_distance_m"]))

print("\n[11] 无效点位：无上游只给 1 格并警告；被 min_area_cells 过滤后整体报错")
dz = cc("corner", "%s,%s" % wpt(0, 0))
check("图幅角上无上游 → 1 格", dz["outlets"][0]["cells"] == 1, str(dz["outlets"][0]["cells"]))
check("给出「不在汇流路径上」的提示", any("single cell" in w for w in dz["warnings"]), str(dz["warnings"]))
dmin = json.loads(T.ras_catchment(vp, "%s,%s" % wpt(0, 0), min_area_cells=10,
                                 out_dir=str(TMP / "c_min")))
check("全部被过滤时返回 error", "error" in dmin, str(dmin)[:80])

print("\n[12] GeoJSON：多边形面积与栅格格数一致（UTM 下 ±1%）")
gj = json.loads(Path(dc["paths"]["catchment_geojson"]).read_text(encoding="utf-8"))
check("单出口 → 1 个要素", len(gj["features"]) == 1, str(len(gj["features"])))
from shapely.geometry import shape as _shape  # noqa: E402

pa_km2 = _shape(gj["features"][0]["geometry"]).area / 1e6
check("多边形面积 ≈ 0.4096 km²", abs(pa_km2 - 0.4096) / 0.4096 < 0.01, f"{pa_km2:.4f}")

print("\n[13] 地貌分类：平地 / 锥顶 / 坑底 / 脊线 / 谷线 / 均匀坡面，逐类核对中心像元")
rr_, cc_ = np.mgrid[0:N, 0:N]
gcases = {
    "g_flat": (np.full((N, N), 100.0), 1),          # 全平
    "g_cone": (300 - np.hypot(rr_ - 32, cc_ - 32) * 3.0, 2),      # 峰
    "g_pit": (np.hypot(rr_ - 32, cc_ - 32) * 3.0, 10),            # 坑
    "g_ridge": (100 - np.abs(cc_ - 32) * 1.0, 3),   # 东西向山脊，脊线在 col=32
    "g_valley": (100 + np.abs(cc_ - 32) * 1.0, 9),  # 东西向谷，谷底在 col=32
    "g_ramp": (cc_ * 1.0, 6),                       # 均匀向东升高
}
for gname, (gdem, want) in gcases.items():
    gd = load(T.ras_geomorphons(write_dem(gname, gdem), search_distance=8,
                                out_dir=str(TMP / gname)))
    with rasterio.open(gd["path"]) as s:
        garr = s.read(1)
    got = int(garr[32, 32])
    check(f"{gname[2:]} 中心像元 = {T.GEOM_CLASSES[want - 1]}",
          got == want, f"得 {T.GEOM_CLASSES[got - 1] if 1 <= got <= 10 else got}")
    check(f"{gname[2:]} 类别码落在 1..10",
          set(np.unique(garr[garr > 0]).tolist()) <= set(range(1, 11)),
          str(np.unique(garr)))

print("\n[14] 地貌分类：参数校验、DEM 空洞、三元模式输出")
gbad = json.loads(T.ras_geomorphons(vp, search_distance=0))
check("search_distance=0 返回 error", "error" in gbad, str(gbad)[:60])
gbad2 = json.loads(T.ras_geomorphons(vp, search_distance=5, skip_distance=5))
check("skip_distance >= search_distance 返回 error", "error" in gbad2, str(gbad2)[:60])

ghole = vv.copy()
ghole[20:30, 20:30] = np.nan
gd = load(T.ras_geomorphons(write_dem("g_hole", ghole), search_distance=8,
                            out_dir=str(TMP / "g_hole")))
with rasterio.open(gd["path"]) as s:
    harr = s.read(1)
check("空洞处输出 0", bool((harr[20:30, 20:30] == 0).all()), str(np.unique(harr[20:30, 20:30])))
check("空洞外全是有效类别", bool((harr[10:15, 10:15] > 0).all()))

gp = load(T.ras_geomorphons(vp, search_distance=8, return_pattern=True,
                            out_dir=str(TMP / "g_pat")))
check("return_pattern 写出模式栅格", Path(gp["paths"]["pattern"]).exists(), str(gp["paths"]))
check("share 之和为 1", abs(sum(gp["share"].values()) - 1.0) < 0.01, str(sum(gp["share"].values())))

print("\n[15] 地貌查找表：上三角 45 个组合全覆盖，关键格与 r.geomorphon 官方图例一致")
tab = T._GEOM_TABLE
check("上三角共 45 个组合", sum(len(r) for r in tab) == 45, str(sum(len(r) for r in tab)))
check("没有空缺（全部已定义）", all(v for r in tab for v in r), str(tab))
for (m, p_), want in {(8, 0): 2, (0, 8): 10, (0, 0): 1, (4, 4): 6,
                      (5, 2): 5, (2, 5): 7, (6, 1): 3, (1, 6): 9}.items():
    got = int(tab[m][p_])
    check(f"向下 {m} / 向上 {p_} → {T.GEOM_CLASSES[want - 1]}",
          got == want, f"得 {T.GEOM_CLASSES[got - 1] if got else got}")

def _fan(lines, n: int) -> np.ndarray:
    """高程 = min(线高程 + 2 m/格 的横向落差)：水先垂直落向河道，再沿河道走。"""
    rr, cc = np.mgrid[0:n, 0:n]
    z = np.full((n, n), 1e6)
    for r0, c0, r1, c1, z0, z1 in lines:
        for t in np.linspace(0, 1, 400):
            z = np.minimum(z, z0 + (z1 - z0) * t + 2.0 * np.hypot(rr - (r0 + (r1 - r0) * t),
                                                                  cc - (c0 + (c1 - c0) * t)))
    return z


def _river_props(res: dict) -> dict:
    g = json.loads(Path(res["paths"]["reaches"]).read_text(encoding="utf-8"))
    return {f["properties"]["reach_id"]: f["properties"] for f in g["features"]}


print("\n[16] 河网：Y 形两条一级支流汇成一条二级干流")
vy = write_dem("riv_y", _fan([(5, 10, 40, 32, 120, 100), (5, 54, 40, 32, 120, 100),
                              (40, 32, 63, 32, 100, 90)], N))
ry = load(T.ras_river_network(vy, river_threshold=40, out_dir=str(TMP / "rn_y")))
py = _river_props(ry)
check("最大 Strahler = 2", ry["stats"]["max_strahler"] == 2, str(ry["stats"]))
check("两条一级 + 一条二级", {k: v["reaches"] for k, v in ry["by_order"].items()} == {"1": 2, "2": 1},
      str(ry["by_order"]))
check("一个汇流点、一个出口、两个源头",
      (ry["stats"]["junctions"], ry["stats"]["outlets"], ry["stats"]["headwaters"]) == (1, 1, 2),
      str(ry["stats"]))
trunk = [i for i, p in py.items() if p["strahler"] == 2][0]
check("干流由两条一级支流汇入", sorted(py[i]["strahler"] for i in py if py[i]["downstream_reach"] == trunk) == [1, 1],
      str([(i, py[i]["strahler"]) for i in py if py[i]["downstream_reach"] == trunk]))
gap = max(py[i]["outlet_elevation_m"] for i in py if py[i]["downstream_reach"] == trunk) \
    - py[trunk]["head_elevation_m"]
check("干流起点紧接支流终点（差一格落差，0–2 m）", 0 <= gap <= 2.0, f"差 {gap:.2f} m")
check("干流出口面积 = 各支流之和（±2%）",
      abs(py[trunk]["upstream_area_km2"] * 1e3 - 0.41 * 1e3) < 10, str(py[trunk]["upstream_area_km2"]))
check("没有图幅截断警告", not ry["warnings"], str(ry["warnings"]))

print("\n[17] 河网：三条一级支流汇入同一点 → 仍为 2 级（取最大，不累加）")
v3 = write_dem("riv_3", _fan([(5, 5, 45, 32, 150, 110), (5, 32, 45, 32, 150, 110),
                              (5, 59, 45, 32, 150, 110), (45, 32, 70, 32, 110, 100)], 72))
r3 = load(T.ras_river_network(v3, river_threshold=40, out_dir=str(TMP / "rn_3")))
check("最大 Strahler = 2（不是 3）", r3["stats"]["max_strahler"] == 2, str(r3["stats"]["max_strahler"]))

print("\n[18] 河网：两个 Y 再合并 → 3 级；拓扑与 Strahler 自洽")
v4 = write_dem("riv_4", _fan([(5, 10, 35, 30, 150, 120), (5, 35, 35, 30, 150, 120),
                              (35, 30, 60, 48, 120, 100), (5, 60, 35, 80, 150, 120),
                              (5, 85, 35, 80, 150, 120), (35, 80, 60, 48, 120, 100),
                              (60, 48, 90, 48, 100, 90)], 96))
r4 = load(T.ras_river_network(v4, river_threshold=40, out_dir=str(TMP / "rn_4")))
p4 = _river_props(r4)
check("最大 Strahler = 3", r4["stats"]["max_strahler"] == 3, str(r4["stats"]["max_strahler"]))
check("只有一个出口", r4["stats"]["outlets"] == 1, str(r4["stats"]["outlets"]))
ups = {i: [j for j, q in p4.items() if q["downstream_reach"] == i] for i in p4}
bad_s = [i for i, q in p4.items()
         if q["strahler"] != (1 if not ups[i] else
                              (max(p4[j]["strahler"] for j in ups[i]) + (1 if len(
                                  {p4[j]["strahler"] for j in ups[i]}) == 1 else 0)))]
bad_m = [i for i, q in p4.items()
         if q["magnitude"] != (1 if not ups[i] else sum(p4[j]["magnitude"] for j in ups[i]))]
check("每条河段的级数都等于上游规则", not bad_s, str(bad_s[:5]))
check("每条河段的 magnitude 等于上游求和", not bad_m, str(bad_m[:5]))
check("出口 magnitude = 源头条数",
      p4[[i for i in p4 if p4[i]["downstream_reach"] is None][0]]["magnitude"]
      == r4["stats"]["headwaters"], str(r4["stats"]))
cycles = []
for i in p4:
    seen, cur = set(), i
    while cur is not None and cur not in seen:
        seen.add(cur)
        cur = p4[cur]["downstream_reach"]
    if cur is not None:
        cycles.append(i)
check("无环、每条河段都能走到出口", not cycles, str(cycles[:5]))
check("上游面积沿下游单调不减",
      all(p4[j]["upstream_area_km2"] <= p4[i]["upstream_area_km2"] + 1e-9
          for i in p4 for j in ups[i]))

print("\n[19] 河网：阈值口径、单河道、错误输入")
rt = r4["threshold"]
check("river_threshold 优先，单位是格", rt["cells"] == 40 and rt["set_by"] == "river_threshold", str(rt))
ra = load(T.ras_river_network(v4, min_area_km2=0.04, out_dir=str(TMP / "rn_area")))
check("min_area_km2 换算成格（0.04 km² / 100 m² = 400 格）",
      ra["threshold"]["cells"] == 400 and ra["threshold"]["set_by"] == "min_area_km2",
      str(ra["threshold"]))
vflat = write_dem("riv_one", (N - np.arange(N))[:, None] * 0.5
                  + np.abs(np.arange(N) - 32)[None, :] * 1.0)                # V 形谷：单一河道
rone = load(T.ras_river_network(vflat, river_threshold=600, out_dir=str(TMP / "rn_one")))
check("V 形谷只出一条河段，且为 1 级",
      rone["stats"]["reaches"] == 1 and rone["stats"]["max_strahler"] == 1, str(rone["stats"]))
check("无汇流时给出提示", any("no confluence" in w for w in rone["warnings"]), str(rone["warnings"]))
bad = json.loads(T.ras_river_network(v4, river_threshold=100000))
check("阈值过高返回 error", "error" in bad, str(bad)[:60])
bad2 = json.loads(T.ras_river_network(v4, river_threshold=1))
check("river_threshold < 2 返回 error", "error" in bad2, str(bad2)[:60])

print("\n[20] 经纬度 DEM：长度按像元尺寸换米，坡度不会算成 89°")
n2, cell2 = 48, 0.0003
row2, col2 = np.mgrid[0:n2, 0:n2]
z2 = (n2 - row2) * 2.0 + np.abs(col2 - 24) * 12.0            # V 形谷，主河道沿第 24 列向南
geo = TMP / "riv_geo.tif"
with rasterio.open(geo, "w", driver="GTiff", height=n2, width=n2, count=1, dtype="float32",
                   crs="EPSG:4326",
                   transform=from_origin(141.0, 36.5, cell2, cell2)) as dst:
    dst.write(z2.astype("float32"), 1)
rg = load(T.ras_river_network(str(geo), river_threshold=30, out_dir=str(TMP / "rn_geo")))
pg = _river_props(rg)
only = list(pg.values())[0]
yres_m = rg["cell_size_m"]["y"]
check("识别为经纬度并换算成米", "geographic" in (rg["cell_size_m"]["note"] or ""), str(rg["cell_size_m"]))
check("长度 = (N-1) × 经向格宽（±2%）",
      abs(only["length_m"] - (n2 - 1) * yres_m) < 0.02 * (n2 - 1) * yres_m,
      f"{only['length_m']} vs {(n2 - 1) * yres_m:.1f}")
check("坡度是度不是 89.99", 0 < only["mean_slope_deg"] < 10, str(only["mean_slope_deg"]))

print("\n[21] HAND：V 形谷上 HAND = 0.5·|列 − 河道列|（有解析解）")
hz = (N - np.arange(N))[:, None] * 0.1 + np.abs(np.arange(N) - 32)[None, :] * 0.5
hv = write_dem("hand_v", hz)
rh = load(T.ras_hand(hv, river_threshold=40, stages="1.7,2.4,3.6", out_dir=str(TMP / "hand_v")))
with rasterio.open(rh["paths"]["hand"]) as s:
    hand = s.read(1)
dc = np.abs(np.arange(N)[None, :] - 32)
check("河道格 HAND = 0", bool((hand[:, 32] == 0).all()), str(hand[:3, 32]))
check("HAND = 0.5·|dc|（误差 < 1e-3）", float(np.abs(hand - 0.5 * dc).max()) < 1e-3,
      f"{np.abs(hand - 0.5 * dc).max():.2e}")
check("识别出的河道只有 64 格（一列）", rh["channel_cells"] == 64, str(rh["channel_cells"]))
check("HAND 分位数与解析一致（中位 8 m）", abs(rh["hand_stats"]["p50"] - 8.0) < 0.1,
      str(rh["hand_stats"]))
for row, expect_cells in zip(rh["stages"], (448, 576, 960)):
    check(f"水位 {row['stage_m']} m 淹没 {expect_cells} 格", row["cells"] == expect_cells,
          str(row["cells"]))
    check(f"水位 {row['stage_m']} m 面积 = 格数 × 100 m²",
          abs(row["area_km2"] - expect_cells * 100 / 1e6) < 1e-9, str(row["area_km2"]))
check("最深水深 = 水位", all(abs(r["max_depth_m"] - r["stage_m"]) < 1e-6 for r in rh["stages"]),
      str([r["max_depth_m"] for r in rh["stages"]]))
check("面积随水位单调不减",
      all(a["cells"] <= b["cells"] for a, b in zip(rh["stages"], rh["stages"][1:])))
check("没有孤立低地被计入", all(r["dropped_unconnected_cells"] == 0 for r in rh["stages"]),
      str([r["dropped_unconnected_cells"] for r in rh["stages"]]))
with rasterio.open(rh["paths"]["inundation_2.4m"]) as s:
    wet = s.read(1) > 0
lab = measure.label(wet, connectivity=2)
river_mask = hand[:, 32] == 0
check("每个淹没斑块都连着河道",
      set(np.unique(lab[wet])) == set(np.unique(lab[np.ix_(np.arange(N), [32])])) ,
      f"{len(set(np.unique(lab[wet])))} 个斑块")
check("淹没区是 HAND < 水位的子集", bool((hand[wet] < 2.4).all()), "")

print("\n[22] HAND：经纬度 DEM 的面积换算与参数校验")
rg2 = load(T.ras_hand(str(geo), river_threshold=30, stages="20", out_dir=str(TMP / "hand_geo")))
with rasterio.open(rg2["paths"]["hand"]) as s:
    hg = s.read(1)
dc2 = np.abs(np.arange(n2)[None, :] - 24)
check("经纬度下 HAND 仍是米（= 12·|dc|）", float(np.abs(hg - 12.0 * dc2).max()) < 1e-3,
      f"{np.abs(hg - 12.0 * dc2).max():.2e}")
row = rg2["stages"][0]
want_area = row["cells"] * rg2["cell_size_m"]["x"] * rg2["cell_size_m"]["y"] / 1e6
check("面积按换算后的格宽计算", abs(row["area_km2"] - want_area) < 1e-3,
      f"{row['area_km2']} vs {want_area:.4f}")
bad3 = json.loads(T.ras_hand(hv, river_threshold=40, stages="0"))
check("水位必须为正", "error" in bad3, str(bad3)[:60])
bad4 = json.loads(T.ras_hand(hv, river_threshold=100000))
check("没有河道格时返回 error", "error" in bad4, str(bad4)[:60])
bad5 = json.loads(T.ras_hand(hv, river_threshold=1))
check("river_threshold < 2 返回 error", "error" in bad5, str(bad5)[:60])

print("\n[23] ras.index：两波段归一化差值，值域与 NoData 处理")
n3 = 24
nir = np.full((n3, n3), 0.6, dtype="float32")
red = np.full((n3, n3), 0.2, dtype="float32")
red[4:8, 4:8] = -0.6                              # 与 NIR 相加为 0 → 比值无定义
two = TMP / "two_band.tif"
with rasterio.open(two, "w", driver="GTiff", height=n3, width=n3, count=2, dtype="float32",
                   crs="EPSG:32654",
                   transform=from_origin(500000, 4000000, CELL, CELL)) as dst:
    dst.write(nir, 1)
    dst.write(red, 2)
ri = load(T.ras_index(str(two), 1, 2, name="ndvi"))
with rasterio.open(ri["out_path"]) as s:
    idx = s.read(1)
check("(0.6-0.2)/(0.6+0.2) = 0.5", bool((idx[np.isfinite(idx)] == 0.5).all()),
      str(np.unique(idx[np.isfinite(idx)])))
check("和为 0 的 16 格写成 NoData", int(np.isnan(idx).sum()) == 16, str(int(np.isnan(idx).sum())))
check("统计只算有效像元", ri["stats"]["valid_ratio"] == round((n3 * n3 - 16) / (n3 * n3), 4),
      str(ri["stats"]["valid_ratio"]))
ri2 = load(T.ras_index(str(two), 2, 1, name="ndvi_rev"))
with rasterio.open(ri2["out_path"]) as s:
    idx2 = s.read(1)
check("交换两波段变号", bool((idx2[np.isfinite(idx2)] == -0.5).all()))
san = load(T.ras_index(str(two), 1, 2, name="NDVI 2024/11"))
check("name 被清洗成合法文件名", "/" not in san["name"] and " " not in san["name"], san["name"])
check("波段越界报错", "error" in json.loads(T.ras_index(str(two), 1, 9)))
check("同一波段报错", "error" in json.loads(T.ras_index(str(two), 2, 2)))

print("\n[24] ras.wetness：均匀东坡上 TWI/SPI/STI 与解析式逐格一致")
wplane = np.tile(np.arange(N) * CELL * 0.1, (N, 1))
rw = load(T.ras_wetness(write_dem("wet_plane", wplane), out_dir=str(TMP / "wet_p")))
twi = read_bands = None
with rasterio.open(rw["paths"]["twi"]) as s:
    twi = s.read(1)
with rasterio.open(rw["paths"]["spi"]) as s:
    spi = s.read(1)
with rasterio.open(rw["paths"]["sti"]) as s:
    sti = s.read(1)
cols = np.arange(2, N - 2)
a_spec = (N - cols) * CELL                              # a = 汇流格数 × 格宽
exp_twi = np.log(a_spec / 0.1)[None, :].repeat(N - 4, axis=0)
exp_spi = np.log(a_spec * 0.1)[None, :].repeat(N - 4, axis=0)
exp_sti = ((a_spec / 22.13) ** 0.6
           * (np.sin(np.arctan(0.1)) / 0.0896) ** 1.3)[None, :].repeat(N - 4, axis=0)
check("TWI = ln(a / tanβ)（误差 < 1e-3）", float(np.abs(twi[2:-2, 2:-2] - exp_twi).max()) < 1e-3,
      f"{np.abs(twi[2:-2, 2:-2] - exp_twi).max():.2e}")
check("SPI = ln(a · tanβ)（误差 < 1e-3）", float(np.abs(spi[2:-2, 2:-2] - exp_spi).max()) < 1e-3,
      f"{np.abs(spi[2:-2, 2:-2] - exp_spi).max():.2e}")
check("STI = (a/22.13)^0.6 (sinβ/0.0896)^1.3（误差 < 1e-3）",
      float(np.abs(sti[2:-2, 2:-2] - exp_sti).max()) < 1e-3,
      f"{np.abs(sti[2:-2, 2:-2] - exp_sti).max():.2e}")
check("解析坡面上没有格子触到坡度下限", rw["params"]["cells_at_slope_floor"] == 0,
      str(rw["params"]["cells_at_slope_floor"]))

rwf = load(T.ras_wetness(write_dem("wet_flat", np.full((N, N), 100.0)),
                         out_dir=str(TMP / "wet_f")))
with rasterio.open(rwf["paths"]["twi"]) as s:
    ftwi = s.read(1)
check("平地上全部触限", rwf["params"]["cells_at_slope_floor"] == N * N,
      str(rwf["params"]["cells_at_slope_floor"]))
check("平地上结果仍是有限值", bool(np.isfinite(ftwi).all()))
check("触限比例高时给出警告", any("slope floor" in w for w in rwf["warnings"]), str(rwf["warnings"]))
rwt = load(T.ras_wetness(write_dem("wet_sub", wplane), indices="twi", out_dir=str(TMP / "wet_s")))
check("indices 只出请求的指数", list(rwt["paths"]) == ["twi"], str(rwt["paths"]))
check("未知指数报错", "error" in json.loads(T.ras_wetness(write_dem("wet_bad", wplane), indices="tpi")))
check("min_slope_deg <= 0 报错",
      "error" in json.loads(T.ras_wetness(write_dem("wet_bad2", wplane), min_slope_deg=0)))

print(f"\n{'='*46}\n通过 {ok}，失败 {failed}\n")
raise SystemExit(1 if failed else 0)
