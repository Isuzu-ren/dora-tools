# `poi.to_vector`

> POI 数据入库

| | |
|---|---|
| 模块 | `poi` · `src/dora/tools/poi.py:631`（5 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Convert POI (Points of Interest) from GeoJSON/Shapefile to a vector GeoJSON file. Optionally filter by name.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `geojson_path` | str | 是 | — | GeoJSON 文件路径 |
| `name` | str | 否 | `None` | 名称 |
| `exact` | bool | 否 | `False` | 是否精确匹配 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `vector_path` | str | Path to output vector GeoJSON |
| `count` | int | Number of features in output |
| `name_filter` | str | The name filter used |

**落盘产物**：`vector_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.poi import poi_to_vector_tool
import json

res = json.loads(poi_to_vector_tool(geojson_path="admin.geojson"))
print(res)
```

```json
{
  "name": "poi.to_vector",
  "arguments": {
    "geojson_path": "admin.geojson"
  }
}
```

## 适用边界

- **相关性**：★★ —— POI 数据入库
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 80-POI-点位](README.md)　·　[工具总表](../../index/INDEX.md)
