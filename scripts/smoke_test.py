#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最小冒烟测试：不需要任何模型权重，验证「阈值 → 面积」这条链能跑通。

    python scripts/smoke_test.py

会临时造一张 64×64 的 GeoTIFF，调用 ras.threshold 与 ras.area，
打印两段 JSON，并在失败时以非零码退出。
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

    print("\n冒烟测试通过：纯算法工具链可用（未涉及任何模型权重）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
