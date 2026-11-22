# `vis.temporal_panel`

> 水情/旱情演变序列（涨水—峰值—退水）

| | |
|---|---|
| 模块 | `vis` · `src/dora/tools/vis.py:1060`（11 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | PIL |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Generate a multi-temporal panel from multiple image paths. Output file is written to a managed location; its path is returned in the result dict as output_path.

## 这个工具做什么

把多个时间的影像拼成一组，看变化过程——涨水、峰值、退水一条线看下来。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `image_paths` | list[str] | 是 | — | 影像路径列表 |
| `labels` | list[str]? | 否 | `None` | 标签列表 |
| `title` | str | 否 | `'Temporal Panel'` | 图标题 |
| `columns` | int | 否 | `2` | — |

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
from dora.tools.vis import temporal_panel_tool
import json

res = json.loads(temporal_panel_tool(image_paths="input.tif"))
print(res)
```

```json
{
  "name": "vis.temporal_panel",
  "arguments": {
    "image_paths": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 水情/旱情演变序列（涨水—峰值—退水）
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

## 已知坑与建议

- **建议**：吃一个影像列表，自动排布。水情/旱情的本质是「随时间怎么变」，这件正好对口。

## 相关工具

- [`vis.before_after_panel`](vis.before_after_panel.md)
- [`ras.area`](../40-栅格分析/ras.area.md)

---

[← 返回 70-制图与报告](README.md)　·　[工具总表](../../index/INDEX.md)
