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

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `trajectory` | list[dict] | 是 | — | 工具调用轨迹（列表，每项含工具名与参数） |
| `pixel_size_m` | float? | 否 | `None` | 像元边长（米）。掩膜无地理参考时必须显式给出 |
| `include_empty_masks` | bool | 否 | `False` | 是否保留空掩膜 |
| `target_classes` | list[int]? | 否 | `None` | 目标类别值列表 |

## 输出

返回 JSON 字符串，字段见源码；产物路径通常在 `mask_path` / `output_path` / `vector_path` 中。

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
