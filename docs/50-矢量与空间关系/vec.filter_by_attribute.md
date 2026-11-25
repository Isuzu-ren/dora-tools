# `vec.filter_by_attribute`

> 按地类/行政区代码筛选

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:3105`（43 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Filter vector features by attribute values. This is useful when a vector file contains mixed feature types and the task only wants a semantic subset, such as hospitals or commercial POIs based on the `types` attribute.

## 这个工具做什么

按属性表里的字段筛要素，比如只看「耕地」，或只看某个县。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_path` | str | 是 | — | 矢量路径（GeoJSON） |
| `attribute_name` | str | 是 | — | 属性字段名 |
| `allowed_values` | list[str] | 是 | — | 允许的取值列表 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `vector_path` | str | 产物路径 |

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_filter_by_attribute
import json

res = json.loads(vec_filter_by_attribute(vector_path="admin.geojson", attribute_name=""input.tif"", allowed_values="input.tif"))
print(res)
```

```json
{
  "name": "vec.filter_by_attribute",
  "arguments": {
    "vector_path": "admin.geojson",
    "attribute_name": "\"input.tif\"",
    "allowed_values": "input.tif"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：images/heatisland/09LD1638/osm/buildings.geojson（79 个建筑面，已转 EPSG:6677）

```json
{
  "vector_path": "<work>/fixtures/buildings.geojson",
  "attribute_name": "type",
  "allowed_values": [
    "residential"
  ]
}
```

### 示例输出

```json
{
  "tool": "vec.filter_by_attribute",
  "vector_path": "<temp_dir>/filtered_by_attribute_fa0de2.geojson",
  "attribute_name": "type",
  "allowed_values": [
    "residential"
  ],
  "total_input": 79,
  "total_filtered": 0
}
```

耗时 0.02 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— 按地类/行政区代码筛选
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
