# `logi.resource_allocation`

> 抢险队伍/物资分配

| | |
|---|---|
| 模块 | `calculate` · `src/dora/tools/calculate.py:693`（33 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Allocate a limited resource (e.g., rescue teams, medical supplies) across multiple demand sites in proportion to their priority/need. Uses a greedy largest-share-first scheme with per-site capacity caps.

## 这个工具做什么

把有限的队伍、物资按需求比例分下去。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `demands` | list[dict] | 是 | — | Each dict has {"id": ..., "need": float, "cap": float (optional)} |
| `total_supply` | float | 是 | — | Total units available |
| `min_per_site` | float | 否 | `0.0` | Minimum allocation per site. Default 0. |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `allocations` | list[dict | Per-site allocation {"id", "need", "allocated"} |
| `allocated_total` | float | Total units actually allocated |
| `unallocated` | float | Units left over |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.calculate import logi_resource_allocation
import json

res = json.loads(logi_resource_allocation(demands="input.tif", total_supply="0.0"))
print(res)
```

```json
{
  "name": "logi.resource_allocation",
  "arguments": {
    "demands": "input.tif",
    "total_supply": "0.0"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

```json
{
  "demands": [],
  "total_supply": 1000.0
}
```

### 示例输出

```json
{
  "tool": "logi.resource_allocation",
  "allocations": [],
  "allocated_total": 0.0,
  "unallocated": 1000.0
}
```

## 适用边界

- **相关性**：★★ —— 抢险队伍/物资分配
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 60-计算与决策](README.md)　·　[工具总表](../../index/INDEX.md)
