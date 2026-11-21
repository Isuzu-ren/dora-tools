# 分类核对表（待确认）

共 **108 件**。需要你确认的是「域名划分」与「件数分配」，确认后我按这张表生成 108 页说明。

| 功能域 | 件数 | 其中 ★★★ | 其中 B/C（需改造或重训） |
|---|---:|---:|---:|
| 10-水体与淹没 | 3 | 3 | 3 |
| 20-承灾体 | 14 | 3 | 14 |
| 30-地形与地表变化 | 5 | 5 | 3 |
| 40-栅格分析 | 15 | 10 | 0 |
| 50-矢量与空间关系 | 24 | 6 | 0 |
| 60-计算与决策 | 15 | 2 | 0 |
| 70-制图与报告 | 13 | 7 | 1 |
| 80-POI-点位 | 8 | 0 | 0 |
| 90-其他感知 | 11 | 0 | 1 |
| **合计** | **108** | **36** | **22** |

三点说明：

1. **`30-地形与地表变化` 只有 5 件**，但把 `ras.slope` / `ras.hillshade` 划了进来（它们只吃 DEM，语义确定）。`ras.diff` 与 `ras.focal_stats` 留在栅格分析，因为它们对任意两期栅格通用。
2. **`10-水体与淹没` 只有 3 件**，但恰好是业务最核心的三个（淹没、水域、航拍水体），且三件全是 B/C 类——域小、权重高，单列。
3. **跨域工具只归主域**：如 `ras.diff` 同时服务地形变化与多期对比，主域记栅格分析，在域 README 里以「相关工具」交叉引用。

## 10-水体与淹没（3 件）

| 工具 | 相关性 | 可迁移性 | 一句话 |
|---|---|---|---|
| `seg.flood` | ★★★ | C（跨分辨率失效） | 洪水淹没范围主入口；两次水体推理再相减 |
| `seg.reservoir` | ★★★ | C（14 波段归一化） | 干旱核心：水域面积萎缩监测；需 14 波段输入 |
| `seg.water_aerial` | ★★★ | C（0.03 m 航拍） | 应急航拍精细淹没边界 |

## 20-承灾体（14 件）

| 工具 | 相关性 | 可迁移性 | 一句话 |
|---|---|---|---|
| `seg.bridge` | ★★ | B（0.5–1 m） | 洪水冲毁桥梁排查的底图 |
| `seg.building_damage` | ★★★ | B（≤1.6 m） | 淹没区房屋灾损统计 |
| `seg.building_damage_aerial` | ★ | C（0.03 m 航拍） | 同上 |
| `seg.building_damage_opt_sar` | ★★★ | B（需 SAR 预处理） | 汛期多云雨，SAR 是唯一可靠手段 |
| `seg.building_destroyed_aerial` | ★ | C（0.03 m 航拍） | 航拍级灾损细查 |
| `seg.building_intact_aerial` | ★ | C（0.03 m 航拍） | 同上 |
| `seg.building_lowres` | ★★ | B（3.46 m 专用） | 大范围承灾体底数（PlanetScope） |
| `seg.harbor` | ★ | B（0.5–1 m） | 内河/沿海码头受影响范围 |
| `seg.reconstruction_building` | ★★ | B（未实测） | 灾后恢复进度监测 |
| `seg.road_damage` | ★★★ | B（≤1.6 m） | 淹没路段 → 通行阻断、抢险路径 |
| `seg.road_debris_aerial` | ★★ | C（0.03 m 航拍） | 航拍道路阻断精细判定 |
| `seg.road_intact_aerial` | ★ | C（0.03 m 航拍） | 同上，做对照 |
| `seg.storage_tank` | ★ | B（0.5–1 m） | 洪水次生风险源（危化品） |
| `seg.vehicle_trapped_aerial` | ★★ | C（0.03 m 航拍） | 应急救援：受困目标 |

## 30-地形与地表变化（5 件）

| 工具 | 相关性 | 可迁移性 | 一句话 |
|---|---|---|---|
| `ras.hillshade` | ★★★ | A | 地形地貌可视化、滑坡/泥石流易发性底图 |
| `ras.slope` | ★★★ | A | 坡度是滑坡模型与汇流分析的基础因子 |
| `seg.landslide_bitemporal` | ★★★ | B（未实测） | 无 DEM 时的替代路径 |
| `seg.landslide_ms` | ★★★ | C（14 波段归一化） | 地形地貌变化主力；必须 14 波段 |
| `seg.vegetation` | ★★★ | B（仅单期） | 旱情：植被覆盖变化、受旱耕地识别 |

## 40-栅格分析（15 件）

| 工具 | 相关性 | 可迁移性 | 一句话 |
|---|---|---|---|
| `mask.compose_multiclass` | ★★ | A | 把「常水体/新增水体/退水」合成一张图 |
| `ras.area` | ★★★ | A | 淹没面积、受旱面积、水域面积 |
| `ras.clip` | ★★ | A | 按流域/行政区裁切 |
| `ras.concat` | ★★★ | A | 构造 14 波段输入（多光谱 + DEM + 坡度）的必经步骤 |
| `ras.count_pixels` | ★★ | A | 面积前的中间量 |
| `ras.diff` | ★★★ | A | 多期差值、DSM−DEM 求相对高度 |
| `ras.focal_stats` | ★★★ | A | 热点检测、平滑、DEM 局部粗糙度 |
| `ras.grid_windows` | ★★★ | A | 面雨量/旱情分区统计的基础 |
| `ras.reproject` | ★★★ | A | 多源数据统一坐标系（国产影像常为 CGCS2000） |
| `ras.resample` | ★★★ | A | 统一 GSD：模型对分辨率敏感，这一步不能省 |
| `ras.sample_point` | ★★ | A | 站点/断面取值 |
| `ras.sample_points` | ★★ | A | 水文站点批量采样 |
| `ras.stats` | ★★★ | A | 水位/温度/降水量的区域统计 |
| `ras.threshold` | ★★★ | A | 最通用的一招：LST/NDVI/水深/降水栅格都能阈值化 |
| `ras.vectorize` | ★★★ | A | 淹没范围出图、与行政区叠加的前提 |

## 50-矢量与空间关系（24 件）

| 工具 | 相关性 | 可迁移性 | 一句话 |
|---|---|---|---|
| `vec.buffer` | ★★★ | A | 河道缓冲带、溃堤影响带、河岸带 |
| `vec.build_graph` | ★★ | A | 通行能力建模 |
| `vec.centroid` | ★★ | A | 灾情中心点 |
| `vec.clip` | ★★ | A | 裁到流域/行政区边界 |
| `vec.connected_components` | ★★ | A | 数淹没片数、损毁建筑栋数 |
| `vec.convex_hull` | ★★ | A | 灾害影响范围包络 |
| `vec.dissolve` | ★★★ | A | 把破碎淹没斑块合成连片淹没区 |
| `vec.filter_by_area` | ★★★ | A | 去掉掩膜噪点，几乎每步都用 |
| `vec.filter_by_attribute` | ★★ | A | 按地类/行政区代码筛选 |
| `vec.filter_by_distance` | ★★ | A | 以水库/险工段为中心的影响范围筛选 |
| `vec.graph_shortest_path` | ★★ | A | 抢险/撤离路径规划 |
| `vec.intersect` | ★★★ | A | 淹没范围 ∩ 耕地/居民地/行政区 |
| `vec.kbuffer` | ★★ | A | 分级影响区（100/500/1000 m） |
| `vec.length` | ★★ | A | 河道长度、道路淹没长度 |
| `vec.max_polygon` | ★★ | A | 找主淹没区/最大灾区 |
| `vec.nearest` | ★★ | A | 受灾点最近的安置点/物资库 |
| `vec.perimeter` | ★★ | A | 水域岸线长度 |
| `vec.pixel_to_world` | ★★ | A | 把图上位置转成可上报的坐标 |
| `vec.point_in_polygon` | ★★★ | A | 站点/村庄是否位于淹没区或风险区 |
| `vec.raster_stats` | ★★★ | A | 流域内平均降水、行政区平均 LST、耕地平均 NDVI |
| `vec.repair_min_edges` | ★★ | A | 断路情况下最小抢通方案 |
| `vec.road_centerline_extraction` | ★★ | A | 路网骨架，用于通行分析 |
| `vec.simplify` | ★★ | A | 矢量过大时压缩，便于发布 |
| `vec.voronoi` | ★ | A | 物资投放点/水文站服务范围 |

## 60-计算与决策（15 件）

| 工具 | 相关性 | 可迁移性 | 一句话 |
|---|---|---|---|
| `calc.add` | ★★ | A | 累计量 |
| `calc.diff` | ★★ | A | 偏差评估 |
| `calc.div` | ★★ | A | 比例、变化率、单位换算 |
| `calc.greater_than` | ★★ | A | 超阈值判定 |
| `calc.mul` | ★★ | A | 面积×深度、权重×分值 |
| `calc.point_distance` | ★★ | A | 站点间距、影响半径 |
| `calc.sub` | ★★ | A | 变化量 |
| `calc.volume` | ★★ | A | 蓄水量、土方量、淹没水量 |
| `calc.weighted_sum` | ★★ | A | 综合旱情指数（降水+温度+土壤湿度加权） |
| `logi.priority_score` | ★★ | A | 受灾点优先级排序 |
| `logi.resource_allocation` | ★★ | A | 抢险队伍/物资分配 |
| `logi.truck_trips` | ★★ | A | 物资/土方运输车次 |
| `tool.chart_data` | ★★ | A | 为柱/折线图准备数据 |
| `tool.loop` | ★★★ | A | 按网格/按行政区批量算，是「分区统计」的编排器 |
| `tool.reduce` | ★★★ | A | 找极值网格（最热/最深/最旱） |

## 70-制图与报告（13 件）

| 工具 | 相关性 | 可迁移性 | 一句话 |
|---|---|---|---|
| `model.summarize` | ★★★ | B（换 LLM 端点） | 值班简报文字；需 API Key，数据出境需评估 |
| `report.extract_evidence` | ★★ | A | 多步结果的自动汇总，不调模型 |
| `vis.add_map_elements` | ★★★ | A | 成品图规范化 |
| `vis.bar_chart` | ★★ | A | 分区统计展示 |
| `vis.before_after_panel` | ★★★ | A | 汛前汛后对比 |
| `vis.damage_map` | ★★★ | A | 预警产品出图 |
| `vis.heatmap` | ★★ | A | 隐患点、报汛站、受灾点密度 |
| `vis.line_chart` | ★★ | A | 水位/面积过程线 |
| `vis.overlay_mask` | ★★★ | A | 淹没范围图 |
| `vis.pie_chart` | ★★ | A | 构成占比 |
| `vis.report_page` | ★★★ | A | 值班简报 |
| `vis.route_map` | ★★ | A | 抢险路线图 |
| `vis.temporal_panel` | ★★★ | A | 水情/旱情演变序列（涨水—峰值—退水） |

## 80-POI-点位（8 件）

| 工具 | 相关性 | 可迁移性 | 一句话 |
|---|---|---|---|
| `poi.damage_population_exposure` | ★★ | A | 受影响人口优先序 |
| `poi.filter_by_attribute` | ★★ | A | 只看医院/学校/水厂 |
| `poi.filter_by_damage` | ★★ | A | 学校/医院受淹排查 |
| `poi.filter_by_intact` | ★ | A | 可用资源点 |
| `poi.group_by` | ★★ | A | 按行政区/地类汇总 |
| `poi.search_by_name` | ★ | A | 按地名定位 |
| `poi.to_vector` | ★★ | A | POI 数据入库 |
| `poi.world_to_pixel` | ★★ | A | 把业务点位对齐到卫星影像 |

## 90-其他感知（11 件）

| 工具 | 相关性 | 可迁移性 | 一句话 |
|---|---|---|---|
| `seg.lava` | ○ | D（业务无关） | 火山专用 |
| `seg.plane` | ○ | D（业务无关） | 无关 |
| `seg.playground` | ○ | D（业务无关） | 仅在「避难场所选址」这类派生任务中有用 |
| `seg.pool_aerial` | ○ | D（业务无关） | 无关 |
| `seg.roundabout` | ○ | D（业务无关） | 无关 |
| `seg.ship` | ○ | D（业务无关） | 内河航运场景可微调后使用 |
| `seg.swimming_pool` | ○ | D（业务无关） | 无关 |
| `seg.tree_fallen_aerial` | ★ | C（0.03 m 航拍） | 台风/洪涝伴生，河道行洪障碍 |
| `seg.tree_standing_aerial` | ○ | D（业务无关） | 对照类别 |
| `seg.vehicle` | ○ | D（业务无关） | 与灾情关联弱 |
| `seg.vehicle_free_aerial` | ○ | D（业务无关） | 对照类别 |
