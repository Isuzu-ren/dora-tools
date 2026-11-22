# `vec.pixel_to_world`

> 把图上位置转成可上报的坐标

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:2303`（34 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | rasterio |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Convert pixel coordinates to world coordinates (WGS84) using a reference GeoTIFF.

## 这个工具做什么

把图上的行列号换算成经纬度，方便上报和在地图上定位。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `raster_path` | str | 是 | — | 栅格路径 |
| `pixel_row` | int | 是 | — | Pixel row coordinate (y) |
| `pixel_col` | int | 是 | — | Pixel column coordinate (x) |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `latitude` | float | Y coordinate in WGS84 |
| `longitude` | float | X coordinate in WGS84 |
| `pixel_row` | int | Input pixel row |
| `pixel_col` | int | Input pixel col |

## 依赖与运行

- 依赖：rasterio
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_pixel_to_world
import json

res = json.loads(vec_pixel_to_world(raster_path="input.tif", pixel_row="1", pixel_col="1"))
print(res)
```

```json
{
  "name": "vec.pixel_to_world",
  "arguments": {
    "raster_path": "input.tif",
    "pixel_row": "1",
    "pixel_col": "1"
  }
}
```

## 适用边界

- **相关性**：★★ —— 把图上位置转成可上报的坐标
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
