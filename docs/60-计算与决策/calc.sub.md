# `calc.sub`

> 变化量

| | |
|---|---|
| 模块 | `calculate` · `src/dora/tools/calculate.py:318`（11 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Subtract two numbers.

## 这个工具做什么

两个数相减，得到差值。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `a` | float | 是 | — | 参与运算的数值或栅格 A |
| `b` | float | 是 | — | 参与运算的数值或栅格 B |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `difference` | float | a - b |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.calculate import calc_sub
import json

res = json.loads(calc_sub(a="0.0", b="0.0"))
print(res)
```

```json
{
  "name": "calc.sub",
  "arguments": {
    "a": "0.0",
    "b": "0.0"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

```json
{
  "a": 1.0,
  "b": 2.0
}
```

### 示例输出

```json
{
  "tool": "calc.sub",
  "difference": -1.0,
  "a": 1.0,
  "b": 2.0
}
```

## 适用边界

- **相关性**：★★ —— 变化量
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 60-计算与决策](README.md)　·　[工具总表](../../index/INDEX.md)
