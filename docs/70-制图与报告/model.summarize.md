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

## 这个工具做什么

让大模型根据前面的图和数字写一段灾情简报文字，可以带图。

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

## 示例

> ⚠️ **构造示意（未实际运行）**：本机缺少该工具所需的外部服务（如 GPT 接口），下面的返回按源码的字段结构手写，仅用于说明「它会返回什么」。

### 示例输入

数据：一个 2 步的轨迹 + 问题文本（示意）

```json
{
  "task_question": "Which district has the most destroyed buildings?",
  "trajectory": [
    {
      "tool": "seg.building_damage",
      "arguments": {
        "post_image_path": "post.png"
      },
      "result": {
        "mask_path": "mask.png"
      }
    },
    {
      "tool": "vis.damage_map",
      "arguments": {
        "base_image_path": "post.png"
      }
    }
  ],
  "image_paths": [],
  "model": "gpt-4o-mini"
}
```

### 示例输出

```json
{
  "tool": "model.summarize",
  "model": "gpt-4o-mini",
  "summary": "Building damage concentrates in the north-western block: 2,073 pixels were classified as totally destroyed and 25,880 as partially damaged, i.e. partial damage dominates.",
  "backend": "gpt"
}
```

> **构造示意**：本机没有 GPT key，这段返回按源码的字段结构手写，未实际调用。真实使用时它会读轨迹里的工具结果与图片，生成一段自然语言结论。

## 适用边界

- **相关性**：★★★ —— 值班简报文字；需 API Key，数据出境需评估
- **可迁移性**：B（换 LLM 端点）
- 需要外部 LLM Key；数据出境需评估，可换本地模型。输出是自然语言简报，不含数值校验。

## 相关工具

- [`report.extract_evidence`](report.extract_evidence.md)
- [`vis.report_page`](vis.report_page.md)

---

[← 返回 70-制图与报告](README.md)　·　[工具总表](../../index/INDEX.md)
