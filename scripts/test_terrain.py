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


def load(res: str, key: str) -> dict:
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

print(f"\n{'='*46}\n通过 {ok}，失败 {failed}\n")
raise SystemExit(1 if failed else 0)
