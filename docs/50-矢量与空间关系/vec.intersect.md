# `vec.intersect`

> 淹没范围 ∩ 耕地/居民地/行政区

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:2014`（120 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Find intersection between two vector datasets (GeoJSON) using vector overlay. Features of one layer that overlap each other (e.g. per-feature buffers) are merged first, so nothing is counted or measured twice.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_a_path` | str | 是 | — | 矢量层 A（GeoJSON） |
| `vector_b_path` | str | 是 | — | 矢量层 B（GeoJSON） |
| `pixel_size_m` | float | 否 | `None` | 像元边长（米）。掩膜无地理参考时必须显式给出 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `intersection_count` | int | Number of intersection pieces (one per pair of intersecting features) |
| `intersecting_a_count` | int | Number of features of the first dataset that intersect the second |
| `intersecting_b_count` | int | Number of features of the second dataset that intersect the first |
| `intersection_area_m2` | float | Total intersection area in square meters |
| `intersection_path` | str | Path to intersection GeoJSON |

**落盘产物**：`intersection_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_intersect
import json

res = json.loads(vec_intersect(vector_a_path="admin.geojson", vector_b_path="admin.geojson"))
print(res)
```

```json
{
  "name": "vec.intersect",
  "arguments": {
    "vector_a_path": "admin.geojson",
    "vector_b_path": "admin.geojson"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 淹没范围 ∩ 耕地/居民地/行政区
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
