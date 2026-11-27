#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最小冒烟测试：不需要任何模型权重，验证几条纯算法链能跑通。

    python scripts/smoke_test.py

会临时造一张 64×64 的 GeoTIFF，依次调用 ras.threshold / ras.area、
ras.terrain / ras.contour、ras.catchment、ras.geomorphons、ras.river_network，
逐条核对数值，失败时以非零码退出。
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TMP = Path(tempfile.mkdtemp(prefix="dora_smoke_"))
# 工具在 import 时读取 --temp_dir，所以必须在此之前塞进 sys.argv
sys.argv = [sys.argv[0], "--temp_dir", str(TMP)]


def main() -> int:
    try:
        import numpy as np
        import rasterio
        from rasterio.transform import Affine
    except ImportError as e:
        print(f"缺少依赖：{e}\n先执行：pip install -e .")
        return 2

    src = TMP / "demo.tif"
    arr = np.tile(np.arange(64, dtype=np.uint8), (64, 1))  # 0..63 递增
    with rasterio.open(src, "w", driver="GTiff", height=64, width=64, count=1,
                       dtype="uint8", crs="EPSG:32650",
                       transform=Affine(10.0, 0, 500000, 0, -10.0, 3000000)) as ds:
        ds.write(arr, 1)

    from dora.tools.analysis import ras_threshold
    from dora.tools.calculate import ras_area

    print("① ras.threshold：把灰度 < 32 的像元选出来（true_value=1）")
    r1 = json.loads(ras_threshold(str(src), 32, op="<", band=1, true_value=1, false_value=0))
    print(json.dumps(r1, ensure_ascii=False, indent=2))
    if r1.get("error"):
        print("阈值化失败")
        return 1

    print("\n② ras.area：按 10 m 像元算面积")
    r2 = json.loads(ras_area(r1["mask_path"], pixel_size_m=10.0))
    print(json.dumps(r2, ensure_ascii=False, indent=2))
    if r2.get("error"):
        print("面积计算失败")
        return 1

    expect = 32 * 64 * 100.0  # 32 列 × 64 行 × 100 m²
    got = float(r2.get("area_m2", -1))
    print(f"\n期望面积 {expect:.0f} m²，实得 {got:.0f} m²")
    if abs(got - expect) > 1e-6:
        print("面积不符，冒烟测试失败")
        return 1

    print("\n③ ras.terrain / ras.contour：在 10% 均匀斜坡上验证坡度与等高线")
    import math

    from dora.tools.terrain import ras_contour, ras_terrain

    dem = TMP / "dem.tif"
    ramp = np.tile(np.arange(64, dtype=np.float64) * 1.0, (64, 1))  # 每像元升 1 m，10 m 像元 → 10%
    with rasterio.open(dem, "w", driver="GTiff", height=64, width=64, count=1,
                       dtype="float32", crs="EPSG:32650",
                       transform=Affine(10.0, 0, 500000, 0, -10.0, 3000000)) as ds:
        ds.write(ramp.astype("float32"), 1)

    r3 = json.loads(ras_terrain(str(dem), attributes="slope"))
    print(json.dumps(r3, ensure_ascii=False, indent=2))
    if r3.get("error"):
        print("地形因子计算失败")
        return 1
    want = math.degrees(math.atan(0.1))
    if abs(r3["stats"]["slope"]["mean"] - want) > 0.5:
        print(f"坡度均值应约 {want:.2f}°，实得 {r3['stats']['slope']['mean']:.2f}°")
        return 1

    r4 = json.loads(ras_contour(str(dem), interval=20.0))
    if r4.get("error") or r4.get("n_lines", 1) < 2:
        print("等高线生成失败")
        return 1
    print(f"\n等高线 {r4['n_lines']} 条，高程 {r4['levels']}")

    print("\n④ ras.catchment：在均匀东高西低的斜坡上，取西侧底角为出水口")
    from dora.tools.terrain import ras_catchment

    # 每格都向西流（code=16），所以最西列的水只汇到本列，第 0 列的集水区就是整列
    x0 = 500000 + 0.5 * 10.0
    y0 = 3000000 - 63.5 * 10.0
    r5 = json.loads(ras_catchment(str(dem), f"{x0},{y0}"))
    print(json.dumps(r5, ensure_ascii=False, indent=2))
    if r5.get("error"):
        print("流域提取失败")
        return 1
    outlet = r5["outlets"][0]
    if outlet["cells"] != 64:
        print(f"集水区应为 64 格（一列），实得 {outlet['cells']} 格")
        return 1
    if abs(outlet["area_km2"] - 64 * 100 / 1e6) > 1e-9:
        print(f"面积不符：{outlet['area_km2']}")
        return 1

    print("\n⑤ ras.geomorphons：均匀坡面上应以「坡」为主")
    from dora.tools.terrain import ras_geomorphons

    r6 = json.loads(ras_geomorphons(str(dem), search_distance=5))
    if r6.get("error"):
        print("地貌分类失败")
        return 1
    if r6["share"]["slope"] < 0.5:
        print(f"均匀坡面上 slope 占比应过半，实得 {r6['share']['slope']:.2f}")
        return 1
    print(f"\nslope 占 {r6['share']['slope'] * 100:.0f}%，共 {len(r6['classes'])} 类")

    print("\n⑥ ras.river_network：单向坡上 64 条平行河道互不相通，全部为 1 级")
    from dora.tools.terrain import ras_river_network

    r7 = json.loads(ras_river_network(str(dem), river_threshold=2))
    if r7.get("error"):
        print("河网提取失败")
        return 1
    if r7["stats"]["reaches"] != 64 or r7["stats"]["max_strahler"] != 1:
        print(f"应有 64 条 1 级河段，实得 {r7['stats']['reaches']} 条、最高 "
              f"{r7['stats']['max_strahler']} 级")
        return 1
    # 每行 63 格河段占 62 步 × 10 m，64 行合计 39.68 km
    if abs(r7["stats"]["total_length_km"] - 39.68) > 0.05:
        print(f"总长应为 39.68 km，实得 {r7['stats']['total_length_km']}")
        return 1
    print(f"\n{r7['stats']['reaches']} 条河段，共 {r7['stats']['total_length_km']} km")

    print("\n冒烟测试通过：阈值→面积、地形因子、等高线、流域提取、地貌分类、河网分级六条链可用（未涉及任何模型权重）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
