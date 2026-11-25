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

## 这个工具做什么

在形状不失真的前提下减少顶点数，让数据变小、加载更快。

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

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：images/heatisland/09LD1638/osm/buildings.geojson（79 个建筑面，已转 EPSG:6677）

```json
{
  "vector_path": "<work>/fixtures/buildings.geojson",
  "tolerance": 0.0001
}
```

[![示例输入](../../examples/50-矢量与空间关系/vec.simplify/in.webp)](../../examples/50-矢量与空间关系/vec.simplify/in.webp)

### 示例输出

```json
{
  "tool": "vec.simplify",
  "output_path": "<temp_dir>/simplified.geojson",
  "input_vertex_count": 758,
  "output_vertex_count": 757
}
```

[![示例输出](../../examples/50-矢量与空间关系/vec.simplify/out.webp)](../../examples/50-矢量与空间关系/vec.simplify/out.webp)

*示例输出*（点击图片看原图）

耗时 0.11 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— 矢量过大时压缩，便于发布
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
