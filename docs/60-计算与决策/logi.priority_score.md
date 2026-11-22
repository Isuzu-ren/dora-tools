# `logi.priority_score`

> 受灾点优先级排序

| | |
|---|---|
| 模块 | `calculate` · `src/dora/tools/calculate.py:644`（31 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Rank a list of items (e.g., affected districts, damaged facilities) by a priority score computed as a weighted combination of criteria. Returns the items sorted from highest to lowest priority. Used to support emergency dispatch decisions.

## 这个工具做什么

给一批受灾点按多个指标打分排序，决定先救谁。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `items` | list[dict] | 是 | — | Candidate items, each a dict of numeric fields |
| `criteria` | dict[str,float] | 是 | — | Mapping from field name to weight |
| `top_k` | int? | 否 | `None` | 取前 k 个 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `ranked` | list[dict | Items sorted by priority score (descending), each |
| `count` | int | Number of items returned |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.calculate import logi_priority_score
import json

res = json.loads(logi_priority_score(items="input.tif", criteria="input.tif"))
print(res)
```

```json
{
  "name": "logi.priority_score",
  "arguments": {
    "items": "input.tif",
    "criteria": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★ —— 受灾点优先级排序
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 60-计算与决策](README.md)　·　[工具总表](../../index/INDEX.md)
