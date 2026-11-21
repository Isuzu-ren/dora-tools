# `calc.point_distance`

> 站点间距、影响半径

| | |
|---|---|
| 模块 | `calculate` · `src/dora/tools/calculate.py:277`（28 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Compute straight-line distance between two pixel coordinates.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `point_a` | list[float] | 是 | — | [row, col] |
| `point_b` | list[float] | 是 | — | [row, col] |
| `pixel_size_m` | float | 否 | `1.0` | 像元边长（米）。掩膜无地理参考时必须显式给出 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `distance_px` | float | Euclidean distance in pixels |
| `distance_m` | float | Euclidean distance in meters |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.calculate import calc_point_distance
import json

res = json.loads(calc_point_distance(point_a="input.tif", point_b="input.tif"))
print(res)
```

```json
{
  "name": "calc.point_distance",
  "arguments": {
    "point_a": "input.tif",
    "point_b": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★ —— 站点间距、影响半径
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 60-计算与决策](README.md)　·　[工具总表](../../index/INDEX.md)
