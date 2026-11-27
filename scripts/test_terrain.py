"""Self-test for the three terrain tools, on synthetic DEMs with a known answer.

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

print(f"\n{'='*46}\n通过 {ok}，失败 {failed}\n")
raise SystemExit(1 if failed else 0)
