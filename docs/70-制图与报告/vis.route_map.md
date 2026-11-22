# `vis.route_map`

> 抢险路线图

| | |
|---|---|
| 模块 | `vis` · `src/dora/tools/vis.py:971`（37 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | PIL |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Render a shortest-path route on a base image, optionally with a damage-mask overlay. Output file is written to a managed location; its path is returned in the result dict as output_path.

## 这个工具做什么

在底图上画出抢险或撤离的路线。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `base_image_path` | str | 是 | — | 底图影像路径 |
| `path_pixels` | list[list[int]] | 是 | — | 路径的像素坐标列表 |
| `title` | str | 否 | `'Intact Route Map'` | 图标题 |
| `pixel_size_m` | float? | 否 | `None` | 像元边长（米）。掩膜无地理参考时必须显式给出 |
| `start_point` | list[int]? | 否 | `None` | 起点 |
| `end_point` | list[int]? | 否 | `None` | 终点 |
| `overlay_mask_path` | str? | 否 | `None` | 叠加掩膜路径 |
| `class_labels` | dict[str,str]? | 否 | `None` | 类别值到名称的映射，用于图例 |
| `alpha` | float | 否 | `0.35` | 叠加透明度（0–1） |
| `route_color` | list[int]? | 否 | `None` | 路径颜色 |
| `route_width` | int | 否 | `5` | 路径线宽 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `output_path` | str | 生成的图片路径（由调用方通过 `output_path` 参数指定） |

## 依赖与运行

- 依赖：PIL
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.vis import route_map_tool
import json

res = json.loads(route_map_tool(base_image_path="input.tif", path_pixels="input.tif"))
print(res)
```

```json
{
  "name": "vis.route_map",
  "arguments": {
    "base_image_path": "input.tif",
    "path_pixels": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★ —— 抢险路线图
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 70-制图与报告](README.md)　·　[工具总表](../../index/INDEX.md)
