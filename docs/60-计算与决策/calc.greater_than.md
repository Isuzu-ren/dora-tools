# `calc.greater_than`

> 超阈值判定

| | |
|---|---|
| 模块 | `calculate` · `src/dora/tools/calculate.py:394`（13 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Compare two numbers and return whether a > b.

## 这个工具做什么

判断一个数有没有超过阈值，返回是或否。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `a` | float | 是 | — | 参与运算的数值或栅格 A |
| `b` | float | 是 | — | 参与运算的数值或栅格 B |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `value` | int | 1 if a > b else 0 |
| `result` | bool | True if a > b else False |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.calculate import calc_greater_than
import json

res = json.loads(calc_greater_than(a="0.0", b="0.0"))
print(res)
```

```json
{
  "name": "calc.greater_than",
  "arguments": {
    "a": "0.0",
    "b": "0.0"
  }
}
```

## 适用边界

- **相关性**：★★ —— 超阈值判定
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 60-计算与决策](README.md)　·　[工具总表](../../index/INDEX.md)
