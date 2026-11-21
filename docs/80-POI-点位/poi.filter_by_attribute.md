# `poi.filter_by_attribute`

> 只看医院/学校/水厂

| | |
|---|---|
| 模块 | `poi` · `src/dora/tools/poi.py:804`（5 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Filter POI results by attribute values. Useful for keeping only specific POI types (e.g., commercial facilities like restaurants, cafes, banks).

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `data` | list[dict] | 是 | — | 输入数据（数组或字典，结构见源码） |
| `attribute_name` | str | 是 | — | 属性字段名 |
| `allowed_values` | list[str] | 是 | — | 允许的取值列表 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `total_input` | int | Total number of input items |
| `total_filtered` | int | Number of items after filtering |
| `attribute_name` | str | The attribute field used for filtering |
| `allowed_values` | list | The allowed values used for filtering |
| `filtered_results` | list | Filtered results matching the allowed values |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.poi import poi_filter_by_attribute_tool
import json

res = json.loads(poi_filter_by_attribute_tool(data="input.tif", attribute_name=""input.tif"", allowed_values="input.tif"))
print(res)
```

```json
{
  "name": "poi.filter_by_attribute",
  "arguments": {
    "data": "input.tif",
    "attribute_name": "\"input.tif\"",
    "allowed_values": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★ —— 只看医院/学校/水厂
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 80-POI-点位](README.md)　·　[工具总表](../../index/INDEX.md)
