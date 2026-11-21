# 60-计算与决策

15 件：纯标量运算 + 决策规则 + 两个编排器。本域不碰空间数据，但决定「算出来的数怎么用」：
面积乘深度得蓄水量、多指标加权得综合旱情指数、按需求比例分配队伍与物资。

`tool.loop` 是这一域的中心：它把「一条链」变成「一个可并行的批处理」，`bind` 能把循环项注入下游参数。
没有它，Agent 只能逐条手写调用，步数会翻几倍。

## 工具速查（15 件）

| 工具 | 相关性 | 可迁移性 | 用途 |
|---|---|---|---|
| [`tool.loop`](tool.loop.md) | ★★★ | A | 按网格/按行政区批量算，是「分区统计」的编排器 |
| [`tool.reduce`](tool.reduce.md) | ★★★ | A | 找极值网格（最热/最深/最旱） |
| [`calc.add`](calc.add.md) | ★★ | A | 累计量 |
| [`calc.diff`](calc.diff.md) | ★★ | A | 偏差评估 |
| [`calc.div`](calc.div.md) | ★★ | A | 比例、变化率、单位换算 |
| [`calc.greater_than`](calc.greater_than.md) | ★★ | A | 超阈值判定 |
| [`calc.mul`](calc.mul.md) | ★★ | A | 面积×深度、权重×分值 |
| [`calc.point_distance`](calc.point_distance.md) | ★★ | A | 站点间距、影响半径 |
| [`calc.sub`](calc.sub.md) | ★★ | A | 变化量 |
| [`calc.volume`](calc.volume.md) | ★★ | A | 蓄水量、土方量、淹没水量 |
| [`calc.weighted_sum`](calc.weighted_sum.md) | ★★ | A | 综合旱情指数（降水+温度+土壤湿度加权） |
| [`logi.priority_score`](logi.priority_score.md) | ★★ | A | 受灾点优先级排序 |
| [`logi.resource_allocation`](logi.resource_allocation.md) | ★★ | A | 抢险队伍/物资分配 |
| [`logi.truck_trips`](logi.truck_trips.md) | ★★ | A | 物资/土方运输车次 |
| [`tool.chart_data`](tool.chart_data.md) | ★★ | A | 为柱/折线图准备数据 |

## 相关但不在本域

- `ras.area` / `ras.count_pixels`（40 / 60）：本域多数输入的来源
- `tool.chart_data` → `vis.bar_chart`（70）：结果出图
- `logi.priority_score` → `poi.damage_population_exposure`（80）：处置排序

## 列的含义

- **相关性**：★★★ 业务直接调用 / ★★ 流程必需 / ★ 特定子场景 / ○ 无交集
- **可迁移性**：A 零改造直迁 / B 加规范可用 / C 必须重训 / D 不建议迁
- 判定依据见 [`01-工具全景`](../01-工具全景.md) 与 [`99-附录/A-接入红线`](../99-附录/A-接入红线.md)
