# `vis.add_map_elements`

> 成品图规范化

| | |
|---|---|
| 模块 | `vis` · `src/dora/tools/vis.py:899`（29 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | PIL |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Add title, legend, north arrow, and scale bar to an image. Output file is written to a managed location; its path is returned in the result dict as output_path.

## 这个工具做什么

给现成的图补上标题、图例、指北针和比例尺，让它看起来像正式产品。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `image_path` | str | 是 | — | 输入栅格路径（GeoTIFF / PNG；PNG 无地理参考） |
| `title` | str? | 否 | `None` | 图标题 |
| `legend_items` | list[dict]? | 否 | `None` | 图例条目 |
| `legend_alpha` | float? | 否 | `None` | 图例透明度 |
| `point_markers` | list[dict]? | 否 | `None` | 点标记样式 |
| `north_arrow` | bool | 否 | `True` | 是否绘制指北针 |
| `scale_bar` | bool | 否 | `True` | 是否绘制比例尺 |
| `pixel_size_m` | float? | 否 | `None` | 像元边长（米）。掩膜无地理参考时必须显式给出 |

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
from dora.tools.vis import add_map_elements_tool
import json

res = json.loads(add_map_elements_tool(image_path="input.tif"))
print(res)
```

```json
{
  "name": "vis.add_map_elements",
  "arguments": {
    "image_path": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 成品图规范化
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 70-制图与报告](README.md)　·　[工具总表](../../index/INDEX.md)
