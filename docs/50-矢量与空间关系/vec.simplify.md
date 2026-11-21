# `vec.simplify`

> 矢量过大时压缩，便于发布

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:4037`（43 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Simplify polygon or line geometries using the Douglas-Peucker algorithm. Reduces the number of vertices while preserving overall shape, producing lighter outputs suitable for visualization or downstream computation.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_path` | str | 是 | — | 矢量路径（GeoJSON） |
| `tolerance` | float | 是 | — | Simplification tolerance in CRS units (meters for projected) |
| `preserve_topology` | bool | 否 | `True` | Default True |
| `out_path` | str? | 否 | `None` | 输出文件路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `output_path` | str | Path to simplified GeoJSON |
| `input_vertex_count` | int | Total vertices in input |
| `output_vertex_count` | int | Total vertices in output |

**落盘产物**：`output_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_simplify
import json

res = json.loads(vec_simplify(vector_path="admin.geojson", tolerance="0.0"))
print(res)
```

```json
{
  "name": "vec.simplify",
  "arguments": {
    "vector_path": "admin.geojson",
    "tolerance": "0.0"
  }
}
```

## 适用边界

- **相关性**：★★ —— 矢量过大时压缩，便于发布
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
