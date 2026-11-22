# `poi.group_by`

> 按行政区/地类汇总

| | |
|---|---|
| 模块 | `poi` · `src/dora/tools/poi.py:655`（5 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Group a list of dictionaries by a field and calculate statistics.

## 这个工具做什么

按某个字段把点位分组计数，比如各县有多少个安置点。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `data` | list[dict] | 是 | — | 输入数据（数组或字典，结构见源码） |
| `group_field` | str | 是 | — | 分组字段 |
| `count_field` | str | 否 | `None` | Field to sum (for weighted counts) |
| `return_item_details` | bool | 否 | `False` | Whether to include items in groups (default: False) |
| `return_sum` | bool | 否 | `False` | Whether to include sum of count_field (default: False) |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `group_field` | str | The field used for grouping |
| `total_items` | int | Total number of input items |
| `total_groups` | int | Number of unique groups |
| `groups` | dict | Dictionary of {group_value: {count}} or {count, sum, items} based on options |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.poi import poi_group_by_tool
import json

res = json.loads(poi_group_by_tool(data="input.tif", group_field=""input.tif""))
print(res)
```

```json
{
  "name": "poi.group_by",
  "arguments": {
    "data": "input.tif",
    "group_field": "\"input.tif\""
  }
}
```

## 适用边界

- **相关性**：★★ —— 按行政区/地类汇总
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 80-POI-点位](README.md)　·　[工具总表](../../index/INDEX.md)
