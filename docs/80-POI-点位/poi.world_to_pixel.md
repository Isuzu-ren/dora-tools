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

## 这个工具做什么

把经纬度换算成影像上的行列号，让业务点位和卫星图对齐。

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

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：Tokyo OSM 点要素（EPSG:4326）；同区域影像 image_opt.tif（EPSG:6677）

```json
{
  "geojson_path": "<work>/fixtures/points_clean.geojson",
  "raster_path": "<DORA_DATA>/images/heatisland/09LD1638/image_opt.tif"
}
```

### 示例输出

```json
{
  "tool": "poi.world_to_pixel",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "osm_id": -2073894183,
        "name": "吉野家",
        "type": "fast_food",
        "pixel_row": 1367,
        "pixel_col": 1525,
        "latitude": 35.6918064,
        "longitude": 139.6954398,
        "utm_x": -12479.940280045586,
        "utm_y": -34183.793230866126,
        "pixel_size_m": 0.8
      },
      "geometry": {
        "type": "Point",
        "coordinates": [
          1525.0,
          1367.0
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "osm_id": -671919646,
        "name": "タリーズコーヒー",
        "type": "cafe",
        "pixel_row": 1360,
        "pixel_col": 1435,
        "latitude": 35.691819,
        "longitude": 139.6952416,
        "utm_x": -12497.87625281864,
        "utm_y": -34182.370152511925,
        "pixel_size_m": 0.8
      },
      "geometry": {
        "type": "Point",
        "coordinates": [
          1435.0,
          1360.0
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "osm_id": -28688425,
        "name": "宇奈とと",
        "type": "restaurant",
        "pixel_row": 1342,
        "pixel_col": 1562,
        "latitude": 35.6918521,
        "longitude": 139.695521,
        "utm_x": -12472.584221742636,
        "utm_y": -34178.73348329756,
        "pixel_size_m": 0.8
      },
      "geometry": {
        "type": "Point",
        "coordinates": [
          1562.0,
          1342.0
        ]
      }
    },
    "…（共 130 条，此处省略）"
  ],
  "output_path": "<temp_dir>/poi_pixel_coords_points_clean.geojs_d5ab81.geojson",
  "total_points": 139,
  "valid_points": 130,
  "filtered_points": 9,
  "image_bounds": {
    "left": -12785.0,
    "right": -12409.0,
    "bottom": -34193.6,
    "top": -33910.2
  },
  "image_size": [
    1880,
    1417
  ],
  "source_crs": "EPSG:4326",
  "target_crs": "EPSG:6677"
}
```

> **输入 GeoJSON 必须是经纬度**：工具内部固定按 EPSG:4326 解释再转成栅格坐标系，喂投影坐标会算出图外的行列号。

耗时 0.08 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— 把业务点位对齐到卫星影像
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 80-POI-点位](README.md)　·　[工具总表](../../index/INDEX.md)
