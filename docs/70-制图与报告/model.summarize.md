# `model.summarize`

> 值班简报文字；需 API Key，数据出境需评估

| | |
|---|---|
| 模块 | `model` · `src/dora/tools/model.py:1037`（11 行） |
| 相关性 | ★★★ |
| 可迁移性 | B（换 LLM 端点） |
| 依赖 | 模型 LLM API |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Use LLM to generate a summary of disaster analysis results.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `task_question` | str | 是 | — | 任务问题文本 |
| `trajectory` | list[dict] | 是 | — | 工具调用轨迹（列表，每项含工具名与参数） |
| `image_paths` | list[str]? | 否 | `None` | 影像路径列表 |
| `final_answer_template` | dict? | 否 | `None` | 最终答案模板 |
| `model` | str | 否 | `GEMINI_MODEL` | 模型名称 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `summary` | str | Natural language summary |
| `image_observations` | list | Short visual observations |
| `key_findings` | list | List of key findings |
| `statistics` | dict | Key statistics |
| `recommendations` | list | Optional recovery or response actions |
| `confidence` | str | Confidence level |

## 依赖与运行

- 依赖：模型 LLM API
- 硬件：需外部 LLM 接口；耗时取决于服务端
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.model import model_summarize_wrapper
import json

res = json.loads(model_summarize_wrapper(task_question=""input.tif"", trajectory="input.tif"))
print(res)
```

```json
{
  "name": "model.summarize",
  "arguments": {
    "task_question": "\"input.tif\"",
    "trajectory": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 值班简报文字；需 API Key，数据出境需评估
- **可迁移性**：B（换 LLM 端点）
- 需要外部 LLM Key；数据出境需评估，可换本地模型。输出是自然语言简报，不含数值校验。

## 相关工具

- [`report.extract_evidence`](report.extract_evidence.md)
- [`vis.report_page`](vis.report_page.md)

---

[← 返回 70-制图与报告](README.md)　·　[工具总表](../../index/INDEX.md)
