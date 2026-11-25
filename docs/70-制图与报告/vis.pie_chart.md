# `vis.pie_chart`

> 构成占比

| | |
|---|---|
| 模块 | `vis` · `src/dora/tools/vis.py:956`（9 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | PIL |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Generate a pie chart from category statistics. Output file is written to a managed location; its path is returned in the result dict as output_path.

## 这个工具做什么

画饼图，看各部分占多大比例。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `data` | dict[str,float] | 是 | — | 输入数据（数组或字典，结构见源码） |
| `title` | str | 否 | `'Pie Chart'` | 图标题 |

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
from dora.tools.vis import pie_chart_tool
import json

res = json.loads(pie_chart_tool(data="input.tif"))
print(res)
```

```json
{
  "name": "vis.pie_chart",
  "arguments": {
    "data": "input.tif"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：损毁掩膜的逐类像元计数

```json
{
  "data": {
    "intact": 1388,
    "partial": 25886,
    "destroyed": 2073
  },
  "output_path": "<work>/pie.png",
  "title": "Damage Composition"
}
```

### 示例输出

```json
{
  "tool": "vis.pie_chart",
  "output_path": "<work>/pie.png",
  "chart_type": "pie",
  "statistics": {
    "intact": 1388,
    "partial": 25886,
    "destroyed": 2073
  },
  "title": "Damage Composition"
}
```

[![占比饼图](../../examples/70-制图与报告/vis.pie_chart/out.webp)](../../examples/70-制图与报告/vis.pie_chart/out.webp)

*占比饼图*（点击图片看原图）

> 类别多于 6 个时颜色会重复，建议先合并小类。

耗时 0.02 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— 构成占比
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 70-制图与报告](README.md)　·　[工具总表](../../index/INDEX.md)
