# `vis.damage_map`

> 预警产品出图

| | |
|---|---|
| 模块 | `vis` · `src/dora/tools/vis.py:934`（16 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | PIL |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Generate a standard damage assessment map. Output file is written to a managed location; its path is returned in the result dict as output_path.

## 这个工具做什么

生成一张规范的灾情专题图：底图、彩色范围、图例、指北针、比例尺一次到位，可以直接发出去。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `base_image_path` | str | 是 | — | 底图影像路径 |
| `overlay_mask_path` | str? | 是 | — | 叠加掩膜路径 |
| `title` | str | 否 | `'Damage Assessment Map'` | 图标题 |
| `pixel_size_m` | float? | 否 | `None` | 像元边长（米）。掩膜无地理参考时必须显式给出 |
| `class_labels` | dict[str,str]? | 否 | `None` | 类别值到名称的映射，用于图例 |
| `alpha` | float | 否 | `0.45` | 叠加透明度（0–1） |

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
from dora.tools.vis import damage_map_tool
import json

res = json.loads(damage_map_tool(base_image_path="input.tif", overlay_mask_path="mask.png"))
print(res)
```

```json
{
  "name": "vis.damage_map",
  "arguments": {
    "base_image_path": "input.tif",
    "overlay_mask_path": "mask.png"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：xbd 灾后影像（0.8 m）；seg.building_damage 掩膜

```json
{
  "base_image_path": "<DORA_DATA>/images/xbd_agent_benchv1/post/guatemala_volcano_00000004_post.png",
  "overlay_mask_path": "<work>/fixtures/mask_damage.tif",
  "output_path": "<work>/damage_map.png",
  "pixel_size_m": 0.8,
  "title": "Guatemala Volcano - Building Damage",
  "class_labels": {
    "1": "Intact",
    "2": "Partial",
    "3": "Destroyed"
  },
  "alpha": 0.45
}
```

[![示例输入](../../examples/70-制图与报告/vis.damage_map/in.webp)](../../examples/70-制图与报告/vis.damage_map/in.webp)

### 示例输出

```json
{
  "tool": "vis.damage_map",
  "output_path": "<work>/damage_map.png",
  "title": "Guatemala Volcano - Building Damage",
  "has_legend": true,
  "legend_alpha": 0.45,
  "point_marker_count": 0,
  "point_marker_labels": [],
  "north_arrow": true,
  "scale_bar": true,
  "layers": [
    "base_image",
    "overlay_mask"
  ]
}
```

[![成品专题图：标题、图例、指北针、比例尺齐全](../../examples/70-制图与报告/vis.damage_map/out.webp)](../../examples/70-制图与报告/vis.damage_map/out.webp)

*成品专题图：标题、图例、指北针、比例尺齐全*（点击图片看原图）

> `pixel_size_m` 只影响比例尺，不改变叠加几何；不传就没有比例尺。

耗时 0.31 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★★ —— 预警产品出图
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

## 已知坑与建议

- **建议**：标准专题图含图例、指北针、比例尺；掩膜先 `ras.vectorize` 再叠，边界更干净。

## 相关工具

- [`vis.overlay_mask`](vis.overlay_mask.md)
- [`vis.add_map_elements`](vis.add_map_elements.md)

---

[← 返回 70-制图与报告](README.md)　·　[工具总表](../../index/INDEX.md)
