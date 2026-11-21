# `ras.sample_points`

> 水文站点批量采样

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:1249`（5 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | rasterio |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Sample pixel values at multiple locations in a raster image.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `image_path` | str | 是 | — | 输入栅格路径（GeoTIFF / PNG；PNG 无地理参考） |
| `points` | list[dict] | 是 | — | 点要素列表 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `total_points` | int | Number of input points |
| `results` | list | List of {row, col, pixel_values, is_inside} for each point |

## 依赖与运行

- 依赖：rasterio
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import ras_sample_points_tool
import json

res = json.loads(ras_sample_points_tool(image_path="input.tif", points="input.tif"))
print(res)
```

```json
{
  "name": "ras.sample_points",
  "arguments": {
    "image_path": "input.tif",
    "points": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★ —— 水文站点批量采样
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 40-栅格分析](README.md)　·　[工具总表](../../index/INDEX.md)
