# `poi.filter_by_damage`

> 学校/医院受淹排查

| | |
|---|---|
| 模块 | `poi` · `src/dora/tools/poi.py:702`（5 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Filter POI results to only include those located in damaged buildings. Takes the output from tool.loop and filters items where damage_class >= 2 (partially damaged or totally destroyed).

## 这个工具做什么

筛出正好落在受损建筑里的点位——被淹的学校、医院就是这么找出来的。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `data` | list[dict] | 是 | — | 输入数据（数组或字典，结构见源码） |
| `min_damage_class` | int | 否 | `2` | Minimum damage class to include (default: 2) |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `total_input` | int | Total number of input items |
| `total_filtered` | int | Number of items after filtering |
| `total_damaged` | int | Number of damaged items found |
| `filtered_results` | list | Filtered results with damage_class >= min_damage_class |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.poi import poi_filter_by_damage_tool
import json

res = json.loads(poi_filter_by_damage_tool(data="input.tif"))
print(res)
```

```json
{
  "name": "poi.filter_by_damage",
  "arguments": {
    "data": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★ —— 学校/医院受淹排查
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 80-POI-点位](README.md)　·　[工具总表](../../index/INDEX.md)
