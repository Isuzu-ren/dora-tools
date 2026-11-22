# `ras.grid_windows`

> 面雨量/旱情分区统计的基础

| | |
|---|---|
| 模块 | `calculate` · `src/dora/tools/calculate.py:132`（49 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | rasterio |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Split a raster image into a uniform n×n grid and return pixel windows. Indexing uses image[x1:x2, y1:y2] where x is row (top→bottom), y is column (left→right). If H or W is not divisible by n, the last row/col expands to the image boundary.

## 这个工具做什么

把一张图切成 n×n 的小格，方便一格一格统计。找「最热的街区」「最旱的片区」，就是先切格再排序。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `image_path` | str | 是 | — | 输入栅格路径（GeoTIFF / PNG；PNG 无地理参考） |
| `n` | int | 是 | — | 数量或网格边长 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `windows` | list[list[int | [[x1,x2,y1,y2], ...] in row-major order |
| `image_shape` | list[int | [height, width] |
| `base_tile_px` | list[int | [floor(H/n), floor(W/n)] |
| `count` | int | n*n |

## 依赖与运行

- 依赖：rasterio
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.calculate import ras_grid_windows
import json

res = json.loads(ras_grid_windows(image_path="input.tif", n="1"))
print(res)
```

```json
{
  "name": "ras.grid_windows",
  "arguments": {
    "image_path": "input.tif",
    "n": "1"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 面雨量/旱情分区统计的基础
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 40-栅格分析](README.md)　·　[工具总表](../../index/INDEX.md)
