# `poi.world_to_pixel`

> 把业务点位对齐到卫星影像

| | |
|---|---|
| 模块 | `poi` · `src/dora/tools/poi.py:680`（5 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | geo+rasterio |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Transform GeoJSON POI coordinates from geographic CRS (WGS84) to the pixel coordinate system of a reference raster image. Points that fall outside the image bounds are filtered out. The output GeoJSON contains the original properties plus pixel coordinates (pixel_row, pixel_col, utm_x, utm_y).

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `geojson_path` | str | 是 | — | GeoJSON 文件路径 |
| `raster_path` | str | 是 | — | 栅格路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `output_path` | str | Path to transformed GeoJSON |
| `total_points` | int | Total input POI count |
| `valid_points` | int | Number of POIs within image bounds |
| `filtered_points` | int | Number of POIs filtered out (outside image) |
| `image_bounds` | dict | Image bounds (left, right, bottom, top) |
| `image_size` | list | [width, height] of the reference image |

**落盘产物**：`output_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：geo+rasterio
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.poi import poi_world_to_pixel_tool
import json

res = json.loads(poi_world_to_pixel_tool(geojson_path="admin.geojson", raster_path="input.tif"))
print(res)
```

```json
{
  "name": "poi.world_to_pixel",
  "arguments": {
    "geojson_path": "admin.geojson",
    "raster_path": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★ —— 把业务点位对齐到卫星影像
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 80-POI-点位](README.md)　·　[工具总表](../../index/INDEX.md)
