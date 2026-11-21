# 20-承灾体

14 件，覆盖建筑、道路、桥梁、车辆、储罐、港口与重建进度，是全库最「重」的一域：
全部依赖 1.31 GB 级的 BitemporalDPT 权重，全部要求灾前 + 灾后配对，全部要求 0.5–1.6 m。

建筑损毁与道路损毁是仅有的两个做过尺度敏感性实测的模型：1.6 m 可用（逐类 IoU 0.43–0.52）、
2.0 m 只能出总量（道路「阻断」只剩 0.23）、3.2 m 中间档塌陷。做灾损统计时请先读
`seg.building_damage` 页的「适用边界」。

## 实测口径

本域 14 件全部依赖模型权重，边界高度一致——先看这张表，再决定读哪一页的细节。

| 工具 | 输入域 | 时相 | 实测 | 可用结论 |
|---|---|---|---|---|
| `seg.building_damage` | 星载光学 0.8 m，3 波段 | 灾前 + 灾后 | **是**（C3：10 景 × 4 尺度） | ≤1.6 m 可用，逐类 IoU 0.43–0.52；2.0 m 只出「是否损毁」；3.2 m 中间档塌陷 |
| `seg.road_damage` | 星载光学 0.5–1 m | 灾前 + 灾后 | **是**（C3） | ≤1.6 m 可用；2.0 m「阻断」面积比 0.23、逐类 IoU 0.193，**不可用** |
| `seg.building_lowres` | 星载 3.46 m | 单期 | 效率（C4） | 3.46 m 专用；71.2 s/MP，512² 约 5.5 GB 内存 |
| `seg.building_damage_opt_sar` | 光学灾前 + SAR 灾后 | 双期（后期限 SAR） | 否 | 需先做辐射定标 / 地理编码 / 斑点滤波，这步不在工具里 |
| `seg.reconstruction_building` | 灾前 + 重建期，约 0.8 m | 双期 | 否 | 与建筑损毁同架构；用于重建进度类指标 |
| `seg.bridge` / `seg.storage_tank` / `seg.harbor` | iSAID 单类，0.5–1 m | 单期 | 否 | 在星载 0.5–1 m 上未验证；内河码头等形态与训练集差异大 |
| `*_aerial` 6 件 | 无人机 0.03 m | 单期 / 双期 | 否 | **星载数据不可用**；只有真实航次时才启用 |

四条共用前提，缺一条结果就不可信：

1. **值域 0–255**：16 位物理量直输会整幅全背景，且不报错（5 景中 4 景全空）。
2. **两期已配准**：双时相模型把灾前灾后拼成 6 通道，错位 1–2 px 就会在边界处制造"损毁"。
3. **切片 518 整数倍**：BitemporalDPT 的窗口写死 518，512 会慢 3.66 倍。
4. **类别值是 1/2/3**：0 是背景，不是"完好"。

> 这 14 件里只有 2 件（建筑、道路）做过完整尺度敏感性实测；其余按代码契约推定，
> 结论方向可靠，但"落在可用还是不可用的边界上"没被验证过。

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
