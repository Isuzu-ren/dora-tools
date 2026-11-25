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

## 这个工具做什么

把一张表格里的点位转成地图上能用的点数据。

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

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：noto 地震 POI（307 个点）

```json
{
  "geojson_path": "<DORA_DATA>/images/disasterm3/noto_earthquake_agent2/noto_earthquake_post_polygon2_poi.geojson",
  "name": "hospital",
  "exact": false
}
```

### 示例输出

```json
{
  "tool": "poi.to_vector",
  "vector_path": "<temp_dir>/poi_vector_noto_earthquake_post_pol_d66ec8.geojson",
  "count": 0,
  "name_filter": "hospital",
  "exact_match": false
}
```

> 按名称筛点并落成新的 GeoJSON；名称匹配是大小写无关的子串匹配。

耗时 0.05 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— POI 数据入库
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 80-POI-点位](README.md)　·　[工具总表](../../index/INDEX.md)
