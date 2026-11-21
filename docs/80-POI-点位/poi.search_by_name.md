# `poi.search_by_name`

> 按地名定位

| | |
|---|---|
| 模块 | `poi` · `src/dora/tools/poi.py:609`（5 行） |
| 相关性 | ★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Search for POI (Points of Interest) by name in a GeoJSON file. Supports both exact and fuzzy matching.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `geojson_path` | str | 是 | — | GeoJSON 文件路径 |
| `name` | str | 是 | — | 名称 |
| `exact` | bool | 否 | `False` | 是否精确匹配 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `search_name` | str | The search term used |
| `features` | list | The found POI features |
| `total_found` | int | Number of POIs matching the search |
| `results` | list | List of matching POIs with name, coordinates, and properties |

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.poi import poi_search_by_name_tool
import json

res = json.loads(poi_search_by_name_tool(geojson_path="admin.geojson", name=""input.tif""))
print(res)
```

```json
{
  "name": "poi.search_by_name",
  "arguments": {
    "geojson_path": "admin.geojson",
    "name": "\"input.tif\""
  }
}
```

## 适用边界

- **相关性**：★ —— 按地名定位
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 80-POI-点位](README.md)　·　[工具总表](../../index/INDEX.md)
