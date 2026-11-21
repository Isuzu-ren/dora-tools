# `ras.stats`

> 水位/温度/降水量的区域统计

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:1275`（40 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | rasterio |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Compute summary statistics for one raster band while ignoring nodata values.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `image_path` | str | 是 | — | 输入栅格路径（GeoTIFF / PNG；PNG 无地理参考） |
| `band` | int | 否 | `1` | 波段号，从 1 开始 |
| `ignore_nodata` | bool | 否 | `True` | Ignore nodata and NaN values. Default is true |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `min` | float|None | Minimum valid value |
| `max` | float|None | Maximum valid value |
| `mean` | float|None | Mean valid value |
| `std` | float|None | Standard deviation of valid values |
| `valid_pixels` | int | Number of valid pixels used |
| `band` | int | Band index used |
| `nodata` | float|None | Raster nodata value |

## 依赖与运行

- 依赖：rasterio
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import ras_stats
import json

res = json.loads(ras_stats(image_path="input.tif"))
print(res)
```

```json
{
  "name": "ras.stats",
  "arguments": {
    "image_path": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 水位/温度/降水量的区域统计
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 40-栅格分析](README.md)　·　[工具总表](../../index/INDEX.md)
