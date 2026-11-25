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

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：images/heatisland/09LD1638/osm/buildings.geojson（79 个建筑面，已转 EPSG:6677）；images/heatisland/09LD1638/image_opt.tif（EPSG:6677）

```json
{
  "vector_path": "<work>/fixtures/buildings.geojson",
  "raster_path": "<DORA_DATA>/images/heatisland/09LD1638/image_opt.tif"
}
```

### 示例输出

```json
{
  "tool": "vec.raster_stats",
  "vector_path": "<work>/fixtures/buildings.geojson",
  "raster_path": "<DORA_DATA>/images/heatisland/09LD1638/image_opt.tif",
  "output_vector_path": "<temp_dir>/buildings_image_opt_stats_819baf_66ead5.geojson",
  "band": 1,
  "stats": [
    "mean",
    "min",
    "max"
  ],
  "feature_count": 72,
  "min_pixels": 1,
  "pixel_area_m2": 0.04000000000000001,
  "feature_stats": [
    {
      "feature_idx": 0,
      "geometry_type": "Polygon",
      "pixel_count": 30246,
      "sampled_area_m2": 1209.8400000000001,
      "osm_id": 312900232,
      "name": "新宿センタービル",
      "type": null,
      "mean": 97.21143291674932,
      "min": 0.0,
      "max": 192.0
    },
    {
      "feature_idx": 1,
      "geometry_type": "Polygon",
      "pixel_count": 2721,
      "sampled_area_m2": 108.84000000000002,
      "osm_id": 572498059,
      "name": null,
      "type": null,
      "mean": 77.93421536199926,
      "min": 51.0,
      "max": 170.0
    },
    {
      "feature_idx": 2,
      "geometry_type": "Polygon",
      "pixel_count": 688,
      "sampled_area_m2": 27.520000000000007,
      "osm_id": 573210046,
      "name": null,
      "type": null,
      "mean": 115.83720930232558,
      "min": 96.0,
      "max": 157.0
    },
    "…（共 72 条，此处省略）"
  ],
  "mean": 113.82445874865175,
  "min": 0.0,
  "max": 255.0
}
```

[![示例输出](../../examples/50-矢量与空间关系/vec.raster_stats/out.webp)](../../examples/50-矢量与空间关系/vec.raster_stats/out.webp)

*示例输出*（点击图片看原图）

耗时 0.65 s（本机 8 核 CPU，无 GPU）。

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
