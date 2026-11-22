# `vec.raster_stats`

> 流域内平均降水、行政区平均 LST、耕地平均 NDVI

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:2888`（154 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | geo+rasterio |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Sample raster values under vector geometries and compute summary statistics. Supports point, line, and polygon geometries. For points, the raster value at the point pixel is used. For non-point geometries, the raster is sampled over covered pixels.

## 这个工具做什么

按行政边界、流域或任意多边形，把图里的数值汇总成一个数。「这个县平均降雨多少」「这个灌区受旱面积多大」都是它算的。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_path` | str | 是 | — | 矢量路径（GeoJSON） |
| `raster_path` | str | 是 | — | 栅格路径 |
| `stats` | list[str] | 否 | `None` | 统计数据字典 |
| `band` | int | 否 | `1` | 波段号，从 1 开始 |
| `return_features` | bool | 否 | `True` | Whether to include per-feature statistics. Default is true |
| `min_pixels` | int | 否 | `1` | Minimum covered pixels required to keep a feature. Default is 1 |
| `all_touched` | bool | 否 | `False` | Whether to rasterize vectors with all_touched=True. Default is false |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `feature_count` | int | Number of features retained after min_pixels filtering |
| `feature_stats` | list[dict], optional | Per-feature statistics |
| `output_vector_path` | str | GeoJSON with attached statistics for retained features |

**落盘产物**：`output_vector_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：geo+rasterio
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_raster_stats
import json

res = json.loads(vec_raster_stats(vector_path="admin.geojson", raster_path="input.tif"))
print(res)
```

```json
{
  "name": "vec.raster_stats",
  "arguments": {
    "vector_path": "admin.geojson",
    "raster_path": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 流域内平均降水、行政区平均 LST、耕地平均 NDVI
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

## 已知坑与建议

- **建议**：唯一支持 `return_features=True` 逐要素返回的统计工具，可直接出表。「XX 县平均降雨」这类问法靠它一件支撑。

## 相关工具

- [`ras.stats`](../40-栅格分析/ras.stats.md)
- [`poi.group_by`](../80-POI-点位/poi.group_by.md)

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
