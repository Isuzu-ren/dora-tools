# `report.extract_evidence`

> 多步结果的自动汇总，不调模型

| | |
|---|---|
| 模块 | `model` · `src/dora/tools/model.py:1004`（13 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | numpy |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Extract structured evidence from intermediate mask outputs in a trajectory.

## 这个工具做什么

从一整段操作记录里，把各步骤算出的面积、时间等关键数字抽出来，汇总成一份清单。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `trajectory` | list[dict] | 是 | — | 工具调用轨迹（列表，每项含工具名与参数） |
| `pixel_size_m` | float? | 否 | `None` | 像元边长（米）。掩膜无地理参考时必须显式给出 |
| `include_empty_masks` | bool | 否 | `False` | 是否保留空掩膜 |
| `target_classes` | list[int]? | 否 | `None` | 目标类别值列表 |

## 输出

返回 JSON 字符串，字段见源码。

## 依赖与运行

- 依赖：numpy
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.model import report_extract_evidence_wrapper
import json

res = json.loads(report_extract_evidence_wrapper(trajectory="input.tif"))
print(res)
```

```json
{
  "name": "report.extract_evidence",
  "arguments": {
    "trajectory": "input.tif"
  }
}
```

## 示例

> ⚠️ **示意输入**：工具确实运行了，但输入与本工具的适用场景不完全对应（如用建筑影像演示滑坡双时相模型），结果只说明「接口怎么用」，不代表精度。

### 示例输入

数据：一段含掩膜产物的轨迹（示意轨迹 + 真实掩膜文件）

```json
{
  "trajectory": [
    {
      "tool": "seg.building_damage",
      "arguments": {
        "post_image_path": "post.png"
      },
      "result": {
        "mask_path": "<work>/fixtures/mask_damage.tif"
      }
    },
    {
      "tool": "ras.area",
      "arguments": {
        "mask_path": "m.tif",
        "pixel_size_m": 0.8
      },
      "result": {
        "area_m2": 16562.0
      }
    }
  ],
  "pixel_size_m": 0.8,
  "include_empty_masks": false,
  "target_classes": [
    1,
    2,
    3
  ]
}
```

### 示例输出

```json
{
  "tool": "report.extract_evidence",
  "total_evidence_items": 0,
  "evidence_items": [],
  "tool_rollup": {},
  "timeline": null,
  "peak_timestamp": null,
  "trend": null,
  "errors": []
}
```

> 它把轨迹里的掩膜折算成面积与类别统计，是「把过程变成证据」的一步。

## 适用边界

- **相关性**：★★ —— 多步结果的自动汇总，不调模型
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

## 已知坑与建议

- **建议**：**不调模型**，纯 numpy 从轨迹里抽结构化证据（各掩膜面积、时序），适合做多步结果的自动汇总。

## 相关工具

- [`model.summarize`](model.summarize.md)
- [`tool.reduce`](../60-计算与决策/tool.reduce.md)

---

[← 返回 70-制图与报告](README.md)　·　[工具总表](../../index/INDEX.md)
