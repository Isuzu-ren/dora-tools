# 90-其他感知

11 件，与本项目基本无关：火山熔岩、飞机、船舶、泳池、操场、环岛、车辆计数，
以及 1 件弱相关（倒伏树木，用于河道行洪障碍排查）。

保留是为了台账完整（108 这个数字要与上游一致）。**每页页首都标注了与本项目的关系**。
另外：其中 10 件共用 `seg_aerial` 与 `seg_isaid` 两份权重，删工具省不出存储。

## 工具速查（11 件）

| 工具 | 相关性 | 可迁移性 | 用途 |
|---|---|---|---|
| [`seg.tree_fallen_aerial`](seg.tree_fallen_aerial.md) | ★ | C（0.03 m 航拍） | 台风/洪涝伴生，河道行洪障碍 |
| [`seg.lava`](seg.lava.md) | ○ | D（业务无关） | 火山专用 |
| [`seg.plane`](seg.plane.md) | ○ | D（业务无关） | 无关 |
| [`seg.playground`](seg.playground.md) | ○ | D（业务无关） | 仅在「避难场所选址」这类派生任务中有用 |
| [`seg.pool_aerial`](seg.pool_aerial.md) | ○ | D（业务无关） | 无关 |
| [`seg.roundabout`](seg.roundabout.md) | ○ | D（业务无关） | 无关 |
| [`seg.ship`](seg.ship.md) | ○ | D（业务无关） | 内河航运场景可微调后使用 |
| [`seg.swimming_pool`](seg.swimming_pool.md) | ○ | D（业务无关） | 无关 |
| [`seg.tree_standing_aerial`](seg.tree_standing_aerial.md) | ○ | D（业务无关） | 对照类别 |
| [`seg.vehicle`](seg.vehicle.md) | ○ | D（业务无关） | 与灾情关联弱 |
| [`seg.vehicle_free_aerial`](seg.vehicle_free_aerial.md) | ○ | D（业务无关） | 对照类别 |

## 相关但不在本域

- 与本项目无关，仅在特定子场景下可能有意义（如台风后的河道行洪障碍）。

## 列的含义

- **相关性**：★★★ 业务直接调用 / ★★ 流程必需 / ★ 特定子场景 / ○ 无交集
- **可迁移性**：A 零改造直迁 / B 加规范可用 / C 必须重训 / D 不建议迁
- 判定依据见 [`01-工具全景`](../01-工具全景.md) 与 [`99-附录/A-接入红线`](../99-附录/A-接入红线.md)
