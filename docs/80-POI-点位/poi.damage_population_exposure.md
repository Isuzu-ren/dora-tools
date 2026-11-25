# `poi.damage_population_exposure`

> 受影响人口优先序

| | |
|---|---|
| 模块 | `poi` · `src/dora/tools/poi.py:897`（21 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Join damage and population feature statistics for POIs and rank exposed locations. Useful for identifying high-population POIs whose damage score exceeds a threshold.

## 这个工具做什么

把受损建筑和人口数据叠在一起，排出「哪个点受影响的人最多」，用于优先处置。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `damage_feature_stats` | list[dict] | 是 | — | Damage stats per POI |
| `population_feature_stats` | list[dict] | 是 | — | Population stats per POI |
| `damage_threshold` | float | 否 | `2.0` | Minimum damage value to keep |
| `damage_field` | str | 否 | `'max'` | 损毁状态字段 |
| `population_field` | str | 否 | `'max'` | 人口数字段 |
| `join_field` | str | 否 | `'name'` | Shared key used to join the two tables |
| `allowed_types` | list[str]? | 否 | `None` | Restrict to POI types if provided |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `total_exposed` | int | Number of POIs above the damage threshold |
| `exposed_pois` | list | Ranked exposed POIs with damage and population values |
| `top_exposed_poi` | dict|None | Highest-priority exposed POI |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.poi import poi_damage_population_exposure_tool
import json

res = json.loads(poi_damage_population_exposure_tool(damage_feature_stats="input.tif", population_feature_stats="input.tif"))
print(res)
```

```json
{
  "name": "poi.damage_population_exposure",
  "arguments": {
    "damage_feature_stats": "input.tif",
    "population_feature_stats": "input.tif"
  }
}
```

## 示例

> ⚠️ **示意输入**：工具确实运行了，但输入与本工具的适用场景不完全对应（如用建筑影像演示滑坡双时相模型），结果只说明「接口怎么用」，不代表精度。

### 示例输入

数据：两个按 name 对齐的属性表（示意数据，结构同 `poi.group_by` 的输出）

```json
{
  "damage_feature_stats": [
    {
      "name": "block_a",
      "max": 3
    },
    {
      "name": "block_b",
      "max": 2
    },
    {
      "name": "block_c",
      "max": 1
    }
  ],
  "population_feature_stats": [
    {
      "name": "block_a",
      "max": 1200
    },
    {
      "name": "block_b",
      "max": 800
    },
    {
      "name": "block_c",
      "max": 450
    }
  ],
  "damage_threshold": 2.0
}
```

### 示例输出

```json
{
  "tool": "poi.damage_population_exposure",
  "join_field": "name",
  "damage_field": "max",
  "population_field": "max",
  "damage_threshold": 2.0,
  "allowed_types": [],
  "total_damage_features": 3,
  "total_population_features": 3,
  "total_exposed": 2,
  "exposed_pois": [
    {
      "name": "block_a",
      "types": null,
      "damage_value": 3.0,
      "population_value": 1200.0,
      "damage_feature_idx": null,
      "population_feature_idx": null
    },
    {
      "name": "block_b",
      "types": null,
      "damage_value": 2.0,
      "population_value": 800.0,
      "damage_feature_idx": null,
      "population_feature_idx": null
    }
  ],
  "top_exposed_poi": {
    "name": "block_a",
    "types": null,
    "damage_value": 3.0,
    "population_value": 1200.0,
    "damage_feature_idx": null,
    "population_feature_idx": null
  }
}
```

> 按 name 做连接，统计受损格网里的人口；真实使用时两个表来自同一套格网。

## 适用边界

- **相关性**：★★ —— 受影响人口优先序
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

## 已知坑与建议

- **建议**：把「范围」翻译成「人和设施」：损毁建筑内的 POI 按人口排序，直接给处置优先级。

## 相关工具

- [`poi.filter_by_damage`](poi.filter_by_damage.md)
- [`logi.priority_score`](../60-计算与决策/logi.priority_score.md)

---

[← 返回 80-POI-点位](README.md)　·　[工具总表](../../index/INDEX.md)
