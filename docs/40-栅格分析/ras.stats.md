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

## 这个工具做什么

给一张图算几个基本数字：最小、最大、平均、以及起伏有多大。用来快速判断这片区域整体什么情况，比如全县平均降雨、平均地表温度。

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

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：Japan_all_14_sentinel.tif 第 4 波段

```json
{
  "image_path": "<DORA_DATA>/images/landslide4sense/Japan_all_14_sentinel.tif",
  "band": 4
}
```

### 示例输出

```json
{
  "tool": "ras.stats",
  "image_path": "<DORA_DATA>/images/landslide4sense/Japan_all_14_sentinel.tif",
  "band": 4,
  "nodata": 0.0,
  "min": 265.0,
  "max": 13001.0,
  "mean": 668.584420944806,
  "std": 270.81311003499343,
  "valid_pixels": 2655360
}
```

> 单波段统计，整幅一次约 1 秒，不走模型。

耗时 0.09 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★★ —— 水位/温度/降水量的区域统计
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 40-栅格分析](README.md)　·　[工具总表](../../index/INDEX.md)
