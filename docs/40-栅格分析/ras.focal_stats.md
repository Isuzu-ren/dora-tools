# `ras.focal_stats`

> 热点检测、平滑、DEM 局部粗糙度

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:3779`（87 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | rasterio |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Compute focal (moving-window) statistics over a raster. For each pixel, aggregate the values inside a square window of side `window_size` centred on the pixel (odd window sizes recommended). Typical uses: smooth a damage density map, detect local hotspots, extract local roughness from a DEM, or pre-process a change map before thresholding. This is the local counterpart of global zonal statistics and is orthogonal to `vec.raster_stats` (which aggregates by vector zones).

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `raster_path` | str | 是 | — | 栅格路径 |
| `statistic` | str | 否 | `'mean'` | 统计量：mean / max / min / std / median |
| `window_size` | int | 否 | `5` | 邻域窗口边长（像元） |
| `nodata` | float? | 否 | `None` | Value to treat as nodata. Defaults to the |
| `out_path` | str? | 否 | `None` | 输出文件路径 |

## 输出

返回 JSON 字符串，字段见源码；产物路径通常在 `mask_path` / `output_path` / `vector_path` 中。

## 依赖与运行

- 依赖：rasterio
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import ras_focal_stats
import json

res = json.loads(ras_focal_stats(raster_path="input.tif"))
print(res)
```

```json
{
  "name": "ras.focal_stats",
  "arguments": {
    "raster_path": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 热点检测、平滑、DEM 局部粗糙度
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 40-栅格分析](README.md)　·　[工具总表](../../index/INDEX.md)
