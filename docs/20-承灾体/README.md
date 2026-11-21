# 20-承灾体

14 件，覆盖建筑、道路、桥梁、车辆、储罐、港口与重建进度，是全库最「重」的一域：
全部依赖 1.31 GB 级的 BitemporalDPT 权重，全部要求灾前 + 灾后配对，全部要求 0.5–1.6 m。

建筑损毁与道路损毁是仅有的两个做过尺度敏感性实测的模型：1.6 m 可用（逐类 IoU 0.43–0.52）、
2.0 m 只能出总量（道路「阻断」只剩 0.23）、3.2 m 中间档塌陷。做灾损统计时请先读
`seg.building_damage` 页的「适用边界」。

## 工具速查（14 件）

| 工具 | 相关性 | 可迁移性 | 用途 |
|---|---|---|---|
| [`seg.building_damage`](seg.building_damage.md) | ★★★ | B（≤1.6 m） | 淹没区房屋灾损统计 |
| [`seg.building_damage_opt_sar`](seg.building_damage_opt_sar.md) | ★★★ | B（需 SAR 预处理） | 汛期多云雨，SAR 是唯一可靠手段 |
| [`seg.road_damage`](seg.road_damage.md) | ★★★ | B（≤1.6 m） | 淹没路段 → 通行阻断、抢险路径 |
| [`seg.bridge`](seg.bridge.md) | ★★ | B（0.5–1 m） | 洪水冲毁桥梁排查的底图 |
| [`seg.building_lowres`](seg.building_lowres.md) | ★★ | B（3.46 m 专用） | 大范围承灾体底数（PlanetScope） |
| [`seg.reconstruction_building`](seg.reconstruction_building.md) | ★★ | B（未实测） | 灾后恢复进度监测 |
| [`seg.road_debris_aerial`](seg.road_debris_aerial.md) | ★★ | C（0.03 m 航拍） | 航拍道路阻断精细判定 |
| [`seg.vehicle_trapped_aerial`](seg.vehicle_trapped_aerial.md) | ★★ | C（0.03 m 航拍） | 应急救援：受困目标 |
| [`seg.building_damage_aerial`](seg.building_damage_aerial.md) | ★ | C（0.03 m 航拍） | 同上 |
| [`seg.building_destroyed_aerial`](seg.building_destroyed_aerial.md) | ★ | C（0.03 m 航拍） | 航拍级灾损细查 |
| [`seg.building_intact_aerial`](seg.building_intact_aerial.md) | ★ | C（0.03 m 航拍） | 同上 |
| [`seg.harbor`](seg.harbor.md) | ★ | B（0.5–1 m） | 内河/沿海码头受影响范围 |
| [`seg.road_intact_aerial`](seg.road_intact_aerial.md) | ★ | C（0.03 m 航拍） | 同上，做对照 |
| [`seg.storage_tank`](seg.storage_tank.md) | ★ | B（0.5–1 m） | 洪水次生风险源（危化品） |

## 相关但不在本域

- `ras.resample`（40-栅格分析）：先把分辨率统一到 ≤1.6 m
- `vec.intersect`（50-矢量与空间关系）：损毁图斑叠行政区/居民地
- `vec.road_centerline_extraction` → `vec.build_graph`（50）：通行阻断分析

## 列的含义

- **相关性**：★★★ 业务直接调用 / ★★ 流程必需 / ★ 特定子场景 / ○ 无交集
- **可迁移性**：A 零改造直迁 / B 加规范可用 / C 必须重训 / D 不建议迁
- 判定依据见 [`01-工具全景`](../01-工具全景.md) 与 [`99-附录/A-接入红线`](../99-附录/A-接入红线.md)
