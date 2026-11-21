# `vis.report_page`

> 值班简报

| | |
|---|---|
| 模块 | `vis` · `src/dora/tools/vis.py:1077`（15 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | PIL |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Compose a one-page disaster report from map, chart, summary, and statistics. Output file is written to a managed location; its path is returned in the result dict as output_path.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `map_image_path` | str? | 是 | — | 地图影像路径 |
| `chart_image_path` | str? | 是 | — | 图表影像路径 |
| `summary_text` | str | 否 | `''` | 摘要文字 |
| `key_statistics` | dict? | 否 | `None` | 关键统计（字典） |
| `title` | str | 否 | `'Disaster Situation Report'` | 图标题 |

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
from dora.tools.vis import report_page_tool
import json

res = json.loads(report_page_tool(map_image_path="input.tif", chart_image_path="input.tif"))
print(res)
```

```json
{
  "name": "vis.report_page",
  "arguments": {
    "map_image_path": "input.tif",
    "chart_image_path": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 值班简报
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 70-制图与报告](README.md)　·　[工具总表](../../index/INDEX.md)
