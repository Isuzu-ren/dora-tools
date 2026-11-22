# `tool.reduce`

> 找极值网格（最热/最深/最旱）

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:639`（56 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Reduce a list of dicts by a numeric field.

## 这个工具做什么

从一批结果里挑出最大、最小或平均值，用来找「最严重的那个」。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `values` | list[dict] | 是 | — | 待归约的数值列表 |
| `field` | str | 是 | — | 参与运算的字段名 |
| `mode` | str | 否 | `'max'` | 归约方式：max / min / mean / sum |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `best_value` | float|None | for max/min |
| `best_index` | int|None | for max/min |
| `best_item` | dict|None | for max/min |
| `mean_value` | float|None | for mean |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import tool_reduce
import json

res = json.loads(tool_reduce(values="input.tif", field=""input.tif""))
print(res)
```

```json
{
  "name": "tool.reduce",
  "arguments": {
    "values": "input.tif",
    "field": "\"input.tif\""
  }
}
```

## 适用边界

- **相关性**：★★★ —— 找极值网格（最热/最深/最旱）
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

## 已知坑与建议

- **建议**：对 `tool.loop` 的结果做 max/min/mean，用来找极值网格（最热、最深、最旱）。

## 相关工具

- [`tool.loop`](tool.loop.md)

---

[← 返回 60-计算与决策](README.md)　·　[工具总表](../../index/INDEX.md)
