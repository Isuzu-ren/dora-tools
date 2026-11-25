# `tool.loop`

> 按网格/按行政区批量算，是「分区统计」的编排器

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:390`（232 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Loop over a list of items and execute a sequence of tool calls for each item. Supports per-item binding and simple step-result references.

## 这个工具做什么

把同一套操作在一个列表上挨个跑一遍，不用手写几十次。按网格、按县逐个统计就靠它。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `calls` | list[dict] | 是 | — | 要循环执行的工具调用列表 |
| `loop_over` | list | 是 | — | 循环遍历的列表（与 calls 配合） |
| `bind` | dict[str,str] | 否 | `None` | 把循环项绑定到下游参数名 |
| `grid_n` | int | 否 | `None` | if loop_over items are windows, provide n to compute row/col |
| `return_all` | bool | 否 | `True` | return per-iteration results |
| `show_progress` | bool | 否 | `True` | — |
| `trajectory` | list[dict] | 否 | `None` | 工具调用轨迹（列表，每项含工具名与参数） |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `results` | list, optional | per-iteration outputs if return_all true |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import tool_loop
import json

res = json.loads(tool_loop(calls="input.tif", loop_over="[]"))
print(res)
```

```json
{
  "name": "tool.loop",
  "arguments": {
    "calls": "input.tif",
    "loop_over": "[]"
  }
}
```

## 示例

> ⚠️ **示意输入**：工具确实运行了，但输入与本工具的适用场景不完全对应（如用建筑影像演示滑坡双时相模型），结果只说明「接口怎么用」，不代表精度。

### 示例输入

数据：同一件工具、两组参数（示意，演示批量调用）

```json
{
  "calls": [
    {
      "tool": "ras.area",
      "args": {
        "mask_path": "<work>/fixtures/mask_landslide.tif",
        "pixel_size_m": 10.0
      }
    }
  ],
  "loop_over": [
    {
      "scene": "japan"
    },
    {
      "scene": "japan"
    }
  ],
  "return_all": false,
  "show_progress": false
}
```

### 示例输出

```json
{
  "tool": "tool.loop",
  "iteration_count": 2,
  "results": []
}
```

> 把「同一工具换参数跑多次」收成一次调用；返回里含每次的结果与汇总。

耗时 0.08 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★★ —— 按网格/按行政区批量算，是「分区统计」的编排器
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

## 已知坑与建议

- **建议**：把一条链变成批处理。实测：IF 模式把每轮平均工具步数从 6.9–9.5 降到 4.6，但分数没变——瓶颈在参数绑定，而 `bind` 正是它的解法。

## 相关工具

- [`tool.reduce`](tool.reduce.md)
- [`tool.chart_data`](tool.chart_data.md)

---

[← 返回 60-计算与决策](README.md)　·　[工具总表](../../index/INDEX.md)
