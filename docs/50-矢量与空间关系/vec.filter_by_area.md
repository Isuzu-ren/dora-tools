# `vec.filter_by_area`

> 去掉掩膜噪点，几乎每步都用

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:3058`（28 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Remove polygons smaller than threshold; useful for cleaning noise.

## 这个工具做什么

把太小的碎块删掉。模型输出常有零星噪点，几百平方米以下的一律当噪声清掉。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_path` | str | 是 | — | 矢量路径（GeoJSON） |
| `min_area_m2` | float | 是 | — | 面积阈值（平方米） |
| `pixel_size_m` | float | 是 | — | 像元边长（米）。掩膜无地理参考时必须显式给出 |

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
from dora.tools.analysis import vec_filter_by_area
import json

res = json.loads(vec_filter_by_area(vector_path="admin.geojson", min_area_m2="0.0", pixel_size_m="0.0"))
print(res)
```

```json
{
  "name": "vec.filter_by_area",
  "arguments": {
    "vector_path": "admin.geojson",
    "min_area_m2": "0.0",
    "pixel_size_m": "0.0"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 去掉掩膜噪点，几乎每步都用
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
