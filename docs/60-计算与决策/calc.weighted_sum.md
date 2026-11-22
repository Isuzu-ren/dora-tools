# `calc.weighted_sum`

> 综合旱情指数（降水+温度+土壤湿度加权）

| | |
|---|---|
| 模块 | `calculate` · `src/dora/tools/calculate.py:602`（23 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Compute a weighted sum over a list of numeric values (multi-criteria aggregation). Commonly used for composite severity indices, e.g., combining building damage, flood depth, and road disruption into one score.

## 这个工具做什么

把几个指标按权重加起来，得到一个综合分。旱情指数、风险评分都是这么合成的。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `values` | list[float] | 是 | — | 待归约的数值列表 |
| `weights` | list[float] | 是 | — | 权重字典 |
| `normalize` | bool | 否 | `False` | If True, normalize weights to sum to 1. Default False. |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `score` | float | Weighted sum |
| `normalized` | bool | Whether weights were normalized |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.calculate import calc_weighted_sum
import json

res = json.loads(calc_weighted_sum(values="input.tif", weights="input.tif"))
print(res)
```

```json
{
  "name": "calc.weighted_sum",
  "arguments": {
    "values": "input.tif",
    "weights": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★ —— 综合旱情指数（降水+温度+土壤湿度加权）
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 60-计算与决策](README.md)　·　[工具总表](../../index/INDEX.md)
