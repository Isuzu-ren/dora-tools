# `ras.sample_point`

> 站点/断面取值

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:1229`（5 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | rasterio |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Sample pixel value at a specific (row, col) location in a raster image.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `image_path` | str | 是 | — | 输入栅格路径（GeoTIFF / PNG；PNG 无地理参考） |
| `row` | int | 是 | — | Pixel row (y coordinate) |
| `col` | int | 是 | — | Pixel column (x coordinate) |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `row` | int | Input row coordinate |
| `col` | int | Input column coordinate |
| `pixel_values` | dict | Pixel value for each band (1-indexed) |
| `is_inside` | bool | Whether the coordinates are within image bounds |

## 依赖与运行

- 依赖：rasterio
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import ras_sample_point_tool
import json

res = json.loads(ras_sample_point_tool(image_path="input.tif", row="1", col="1"))
print(res)
```

```json
{
  "name": "ras.sample_point",
  "arguments": {
    "image_path": "input.tif",
    "row": "1",
    "col": "1"
  }
}
```

## 适用边界

- **相关性**：★★ —— 站点/断面取值
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 40-栅格分析](README.md)　·　[工具总表](../../index/INDEX.md)
