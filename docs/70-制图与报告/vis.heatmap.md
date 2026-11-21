# `vis.heatmap`

> 隐患点、报汛站、受灾点密度

| | |
|---|---|
| 模块 | `vis` · `src/dora/tools/vis.py:1117`（82 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | PIL+scipy |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Render a 2D heatmap visualizing the spatial density of input points or polygon centroids. Uses Gaussian kernel density estimation and a color-mapped overlay. If the input vector contains polygons (e.g., building damage outlines), their centroids are computed automatically.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `points_path` | str | 是 | — | 点要素文件（GeoJSON） |
| `base_image_path` | str? | 否 | `None` | 底图影像路径 |
| `bandwidth` | float? | 否 | `None` | 核密度带宽 |
| `colormap` | str | 否 | `'hot'` | 色带名称 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `heatmap_path` | str | Path to rendered heatmap image |
| `point_count` | int | Number of points used (polygon centroids count as points) |

**落盘产物**：`heatmap_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：PIL+scipy
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.vis import vis_heatmap
import json

res = json.loads(vis_heatmap(points_path="input.tif"))
print(res)
```

```json
{
  "name": "vis.heatmap",
  "arguments": {
    "points_path": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★ —— 隐患点、报汛站、受灾点密度
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 70-制图与报告](README.md)　·　[工具总表](../../index/INDEX.md)
