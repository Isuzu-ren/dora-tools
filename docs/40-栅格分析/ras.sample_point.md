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

## 这个工具做什么

给一个坐标，返回那里图上的数值。想查某个水文站、某个村口的水深或温度，就用它。

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

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：images/landslide4sense/Japan_all_14_sentinel.tif（12 波段，EPSG:4326）

```json
{
  "image_path": "<DORA_DATA>/images/landslide4sense/Japan_all_14_sentinel.tif",
  "row": 512,
  "col": 512
}
```

[![示例输入](../../examples/40-栅格分析/ras.sample_point/in.webp)](../../examples/40-栅格分析/ras.sample_point/in.webp)

### 示例输出

```json
{
  "tool": "ras.sample_point",
  "row": 512,
  "col": 512,
  "pixel_values": {
    "1": 1332,
    "2": 981,
    "3": 935,
    "4": 755,
    "5": 1249,
    "6": 1958,
    "7": 2280,
    "8": 2700,
    "9": 872,
    "10": 16,
    "11": 2093,
    "12": 1122
  },
  "is_inside": true
}
```

耗时 0.08 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— 站点/断面取值
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 40-栅格分析](README.md)　·　[工具总表](../../index/INDEX.md)
