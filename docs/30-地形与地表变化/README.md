# 30-地形与地表变化

12 件：3 个模型（两个滑坡、一个植被）+ 9 个 DEM 派生（坡度、山影，以及**本地新增**的
`ras.terrain`、`ras.geomorphons`、`ras.flow`、`ras.catchment`、`ras.river_network`、`ras.hand`、`ras.contour`）。

地形变化这条需求由本域加栅格分析的 `ras.diff` 共同闭环：两期 DEM 相减得高程变化（填挖、淤积、冲刷），
单期 DEM 出坡度、坡向、曲率与起伏形态，再叠加双时相滑坡模型得图斑。**上游版本只有坡度与山影两个因子，
`ras.terrain` 把地形因子扩到 6 个，`ras.geomorphons` 把「连续的地形因子」推进到「离散的地貌单元」，
`ras.flow` 补上了填洼—流向—汇流这条水文地形链，`ras.catchment` 再往前一步：给定出水口反查上游汇水区，
`ras.river_network` 再把汇流面切成**带 Strahler 分级的矢量河段**——洪水演进与水质模型要的正是这个单元，
`ras.hand` 最后一步把河网与 DEM 合成「水位涨到 X 米、哪里被淹」**，流域提取、河网拓扑与淹没筛查因此
都可以在本域直接完成，不必再外挂 GIS 软件。仍缺的是河道断面、冲淤量这类专业算子，
以及地貌的**成因**类型（喀斯特、冰川、风成）——geomorphon 只描述形态，不回答成因。

## 实测口径

12 件里 3 件是模型、9 件是纯算法，边界完全不同，别混着看。

| 工具 | 输入域 | 时相 | 实测 | 可用结论 |
|---|---|---|---|---|
| `seg.landslide_ms` | 14 波段（S2 12 + 坡度 + DEM），10 m | 单期 | **是**（C1：245 景） | 域内 IoU 0.262，**这是上界不是泛化**；波段数不对会抛错 |
| `seg.landslide_bitemporal` | 3 波段，0.59 m | 双期 | 否 | 不需要 DEM，是没有地形数据时的替代路径 |
| `seg.vegetation` | 3 波段，0.5–1 m | **仅单期** | **是**（C3.3 / C4） | 两期相减平均变化 37.4%，会把模型漂移当灾损；输出是 0/255 |
| `ras.slope` | DEM 单波段 | 单期 | — | 纯算法，Horn 1981，结果只取决于输入数值 |
| `ras.hillshade` | DEM 单波段 | 单期 | — | 纯算法，纯可视化用途 |
| `ras.terrain` ★新增 | DEM 单波段（米） | 单期 | **是**（合成 DEM，全库 111 项断言） | 坡度/坡向/曲率/TRI/TPI/粗糙度；**经纬度 DEM 会按纬度换算米**，不会再出现 86° |
| `ras.flow` ★新增 | DEM 单波段（米） | 单期 | **是**（合成 + 真实 DEM） | 填洼—D8 流向—汇流；平坦区靠 ε 梯度排水，内部无死水格 |
| `ras.geomorphons` ★新增 | DEM 单波段（米） | 单期 | **是**（6 类合成地形 + 真实 DEM） | 10 类地貌单元；类别取决于 `search_distance`，10 格与 30 格结果不同是设计而非缺陷 |
| `ras.catchment` ★新增 | DEM 单波段（米）+ 出水口坐标 | 单期 | **是**（合成 V 形谷 + 真实 DEM） | 给定出水口反查上游汇水区；输出标签栅格 + 多边形，并回报「有多少格触到图幅边界」 |
| `ras.river_network` ★新增 | DEM 单波段（米） | 单期 | **是**（合成 Y 形 / 三级分叉 + 真实 DEM） | 汇流面切成河段并做 Strahler 分级；级数只在图幅内成立，出图口会单独标出 |
| `ras.hand` ★新增 | DEM 单波段（米）+ 一组水位 | 单期 | **是**（V 形谷解析解 + 真实 DEM） | 高出最近河道多少米；给定水位出淹没范围与水位–面积曲线，只算连通河道的水 |
| `ras.contour` ★新增 | DEM 单波段 | 单期 | **是**（斜坡 + 真实 DEM） | 输出 GeoJSON 等值线，带 `elevation` 属性，可直接进 GIS |

地形变化要闭环，还差一步两期 DEM 相减——用 `ras.diff`（在 40-栅格分析域）。

## 工具速查（12 件）

| 工具 | 相关性 | 可迁移性 | 用途 |
|---|---|---|---|
| [`ras.catchment`](ras.catchment.md) | ★★★ | A | 给定出水口反查上游汇水区，洪水预报的单元划分 |
| [`ras.flow`](ras.flow.md) | ★★★ | A | 填洼→流向→汇流，流域提取与洪水演进的前置 |
| [`ras.geomorphons`](ras.geomorphons.md) | ★★★ | A | 10 类地貌单元分类，地貌分区与易发性解释变量 |
| [`ras.hand`](ras.hand.md) | ★★★ | A | 给定水位出淹没范围与水位–面积曲线，零权重的洪水筛查 |
| [`ras.hillshade`](ras.hillshade.md) | ★★★ | A | 地形地貌可视化、滑坡/泥石流易发性底图 |
| [`ras.river_network`](ras.river_network.md) | ★★★ | A | 河网矢量化为河段并做 Strahler 分级，洪水演进与水质的基本单元 |
| [`ras.slope`](ras.slope.md) | ★★★ | A | 坡度是滑坡模型与汇流分析的基础因子 |
| [`ras.terrain`](ras.terrain.md) | ★★★ | A | 一次出坡度/坡向/曲率/TRI/TPI/粗糙度，地形地貌分析的地基 |
| [`seg.landslide_bitemporal`](seg.landslide_bitemporal.md) | ★★★ | B（未实测） | 无 DEM 时的替代路径 |
| [`seg.landslide_ms`](seg.landslide_ms.md) | ★★★ | C（14 波段归一化） | 地形地貌变化主力；必须 14 波段 |
| [`seg.vegetation`](seg.vegetation.md) | ★★★ | B（仅单期） | 旱情：植被覆盖变化、受旱耕地识别 |
| [`ras.contour`](ras.contour.md) | ★★ | A | 等高线出图、坡度分级底图 |

## 相关但不在本域

- `ras.diff`（40-栅格分析）：两期 DEM 相减求高程变化
- `ras.focal_stats`（40）：地形粗糙度
- `ras.threshold` + `ras.area`：变化超阈值区 → 面积

## 列的含义

- **相关性**：★★★ 业务直接调用 / ★★ 流程必需 / ★ 特定子场景 / ○ 无交集
- **可迁移性**：A 零改造直迁 / B 加规范可用 / C 必须重训 / D 不建议迁
- 判定依据见 [`01-工具全景`](../01-工具全景.md) 与 [`99-附录/A-接入红线`](../99-附录/A-接入红线.md)
