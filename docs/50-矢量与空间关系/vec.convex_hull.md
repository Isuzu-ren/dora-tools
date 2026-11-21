# `vec.convex_hull`

> 灾害影响范围包络

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:3887`（30 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Compute the convex hull of a set of polygons or points in a GeoJSON file. Useful for estimating the spatial envelope of a damage cluster or hazard spread footprint.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_path` | str | 是 | — | 矢量路径（GeoJSON） |
| `out_path` | str? | 否 | `None` | 输出文件路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `output_path` | str | Path to convex hull GeoJSON |
| `area_m2` | float | Area of the hull (if CRS is projected) |
| `vertex_count` | int | Number of vertices in the hull |

**落盘产物**：`output_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_convex_hull
import json

res = json.loads(vec_convex_hull(vector_path="admin.geojson"))
print(res)
```

```json
{
  "name": "vec.convex_hull",
  "arguments": {
    "vector_path": "admin.geojson"
  }
}
```

## 适用边界

- **相关性**：★★ —— 灾害影响范围包络
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
