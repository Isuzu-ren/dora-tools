# `tool.chart_data`

> 为柱/折线图准备数据

| | |
|---|---|
| 模块 | `calculate` · `src/dora/tools/calculate.py:432`（115 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Build chart-ready key/value data from a list of records or a dict of records. Useful for converting loop outputs or feature statistics into dynamic inputs for vis.bar_chart / vis.line_chart.

## 这个工具做什么

把一串数值整理成画图要的格式，交给柱状图、折线图去画。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `values` | list | dict | 是 | — | 待归约的数值列表 |
| `value_field` | str | 是 | — | nested field path containing the numeric value |
| `label_field` | str? | 否 | `None` | nested field path for the primary label |
| `fallback_label_field` | str? | 否 | `None` | fallback nested field path when label_field is empty |
| `fallback_label_prefix` | str | 否 | `''` | prefix for fallback label |
| `label_template` | str? | 否 | `None` | template such as "r{item.row_idx}c{item.col_idx}" |
| `sort_by` | str? | 否 | `None` | nested field path to sort by; if omitted, preserves input order |
| `descending` | bool | 否 | `True` | sort order, default True |
| `top_k` | int? | 否 | `None` | 取前 k 个 |
| `round_digits` | int? | 否 | `None` | round numeric values for chart display |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `data` | dict | ordered chart-ready mapping |
| `records` | list[dict | ordered label/value records |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.calculate import tool_chart_data
import json

res = json.loads(tool_chart_data(values="input.tif", value_field=""input.tif""))
print(res)
```

```json
{
  "name": "tool.chart_data",
  "arguments": {
    "values": "input.tif",
    "value_field": "\"input.tif\""
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

```json
{
  "values": [
    3.0,
    4.0,
    5.0
  ],
  "value_field": "score"
}
```

### 示例输出

```json
{
  "tool": "tool.chart_data",
  "data": {},
  "records": [],
  "source_count": 0,
  "kept_count": 0,
  "value_field": "score",
  "sort_by": null,
  "descending": true
}
```

## 适用边界

- **相关性**：★★ —— 为柱/折线图准备数据
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 60-计算与决策](README.md)　·　[工具总表](../../index/INDEX.md)
