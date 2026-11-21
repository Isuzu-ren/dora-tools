# `ras.concat`

> 构造 14 波段输入（多光谱 + DEM + 坡度）的必经步骤

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:1781`（105 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | rasterio |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Concatenate multiple rasters along the band/channel dimension into a single GeoTIFF. All inputs must have identical height/width and, if present, the same CRS and transform.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `image_path_list` | list[str] | 是 | — | list of raster paths (GeoTIFF/COG/…) |
| `dim` | str | 否 | `'bands'` | only "bands" or "channels" is supported for now |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `output_path` | str | Path to the concatenated GeoTIFF in TEMP_DIR |
| `bands` | int | total bands in the output |
| `band_map` | list[dict | [{path, in_bands, out_start_band, out_end_band}] |

**落盘产物**：`output_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：rasterio
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import ras_concat
import json

res = json.loads(ras_concat(image_path_list="input.tif"))
print(res)
```

```json
{
  "name": "ras.concat",
  "arguments": {
    "image_path_list": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 构造 14 波段输入（多光谱 + DEM + 坡度）的必经步骤
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

## 已知坑与建议

- **建议**：构造 14 波段输入的**唯一途径**。顺序必须是 B1–B12、坡度、DEM，错序不报错但结果偏移。

## 相关工具

- [`seg.landslide_ms`](../30-地形与地表变化/seg.landslide_ms.md)
- [`seg.reservoir`](../10-水体与淹没/seg.reservoir.md)

---

[← 返回 40-栅格分析](README.md)　·　[工具总表](../../index/INDEX.md)
