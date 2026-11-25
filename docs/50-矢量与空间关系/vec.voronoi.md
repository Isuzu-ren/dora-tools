# `vec.voronoi`

> 物资投放点/水文站服务范围

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:3934`（40 行） |
| 相关性 | ★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Compute a Voronoi diagram (service-area partition) from a set of input points. Each resulting polygon contains all locations closer to its seed point than to any other. Useful for assigning hospital/firestation service areas.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `points_path` | str | 是 | — | 点要素文件（GeoJSON） |
| `boundary_path` | str? | 否 | `None` | Optional boundary polygon to clip the diagram |
| `out_path` | str? | 否 | `None` | 输出文件路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `output_path` | str | Path to Voronoi polygons GeoJSON |
| `cell_count` | int | Number of Voronoi cells generated |

**落盘产物**：`output_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_voronoi
import json

res = json.loads(vec_voronoi(points_path="input.tif"))
print(res)
```

```json
{
  "name": "vec.voronoi",
  "arguments": {
    "points_path": "input.tif"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：Tokyo OSM 点要素 + 用作边界的建筑面

```json
{
  "points_path": "<work>/fixtures/points.geojson",
  "boundary_path": "<work>/fixtures/buildings.geojson"
}
```

### 示例输出

```json
{
  "tool": "vec.voronoi",
  "output_path": "<temp_dir>/voronoi.geojson",
  "cell_count": 90
}
```

[![泰森多边形（每个点的影响范围）](../../examples/50-矢量与空间关系/vec.voronoi/out.webp)](../../examples/50-矢量与空间关系/vec.voronoi/out.webp)

*泰森多边形（每个点的影响范围）*（点击图片看原图）

> 边界决定裁剪范围；点太少时多边形会很大，注意配合边界使用。

耗时 0.06 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★ —— 物资投放点/水文站服务范围
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
