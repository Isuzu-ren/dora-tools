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

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_path` | str | 是 | — | 矢量路径（GeoJSON） |
| `attribute_name` | str | 是 | — | 属性字段名 |
| `allowed_values` | list[str] | 是 | — | 允许的取值列表 |

## 输出

返回 JSON 字符串，字段见源码；产物路径通常在 `mask_path` / `output_path` / `vector_path` 中。

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

## 适用边界

- **相关性**：★★ —— 按地类/行政区代码筛选
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
