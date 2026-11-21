# `ras.area`

> 淹没面积、受旱面积、水域面积

| | |
|---|---|
| 模块 | `calculate` · `src/dora/tools/calculate.py:85`（27 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | numpy |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Calculate the area of regions in a mask. Only supports pixel-based masks.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `mask_path` | str | 是 | — | 掩膜路径（二值或多类） |
| `pixel_size_m` | float | 是 | — | 像元边长（米）。掩膜无地理参考时必须显式给出 |
| `classes` | list[int]? | 否 | `None` | 要保留的类别值列表 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `area_m2` | float | Total area in square meters |
| `pixel_count` | int | Number of pixels counted |

## 依赖与运行

- 依赖：numpy
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.calculate import ras_area
import json

res = json.loads(ras_area(mask_path="mask.png", pixel_size_m="0.0"))
print(res)
```

```json
{
  "name": "ras.area",
  "arguments": {
    "mask_path": "mask.png",
    "pixel_size_m": "0.0"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 淹没面积、受旱面积、水域面积
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

## 已知坑与建议

- **建议**：面积 = 像元数 × 像元面积。若掩膜是 PNG（无地理参考），必须显式传 `pixel_size_m`，否则数字没有意义。

## 相关工具

- [`ras.count_pixels`](ras.count_pixels.md)
- [`ras.vectorize`](ras.vectorize.md)

---

[← 返回 40-栅格分析](README.md)　·　[工具总表](../../index/INDEX.md)
