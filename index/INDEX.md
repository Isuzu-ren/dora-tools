# 111 件工具总表

其中上游 DORA 108 件，本仓库新增 3 件（标 ★）。
按功能域排序。完整字段见 `index/tools.json`，可交互版本见 `index/index.html`。

| # | 域 | 工具 | 相关性 | 可迁移性 | 用途 |
|---:|---|---|---|---|---|
| 1 | 20-承灾体 | [`seg.bridge`](../docs/20-承灾体/seg.bridge.md) | ★★ | B（0.5–1 m） | 洪水冲毁桥梁排查的底图 |
| 2 | 20-承灾体 | [`seg.building_damage`](../docs/20-承灾体/seg.building_damage.md) | ★★★ | B（≤1.6 m） | 淹没区房屋灾损统计 |
| 3 | 20-承灾体 | [`seg.building_damage_aerial`](../docs/20-承灾体/seg.building_damage_aerial.md) | ★ | C（0.03 m 航拍） | 同上 |
| 4 | 20-承灾体 | [`seg.building_damage_opt_sar`](../docs/20-承灾体/seg.building_damage_opt_sar.md) | ★★★ | B（需 SAR 预处理） | 汛期多云雨，SAR 是唯一可靠手段 |
| 5 | 20-承灾体 | [`seg.building_destroyed_aerial`](../docs/20-承灾体/seg.building_destroyed_aerial.md) | ★ | C（0.03 m 航拍） | 航拍级灾损细查 |
| 6 | 20-承灾体 | [`seg.building_intact_aerial`](../docs/20-承灾体/seg.building_intact_aerial.md) | ★ | C（0.03 m 航拍） | 同上 |
| 7 | 20-承灾体 | [`seg.building_lowres`](../docs/20-承灾体/seg.building_lowres.md) | ★★ | B（3.46 m 专用） | 大范围承灾体底数（PlanetScope） |
| 8 | 20-承灾体 | [`seg.harbor`](../docs/20-承灾体/seg.harbor.md) | ★ | B（0.5–1 m） | 内河/沿海码头受影响范围 |
| 9 | 20-承灾体 | [`seg.reconstruction_building`](../docs/20-承灾体/seg.reconstruction_building.md) | ★★ | B（未实测） | 灾后恢复进度监测 |
| 10 | 20-承灾体 | [`seg.road_damage`](../docs/20-承灾体/seg.road_damage.md) | ★★★ | B（≤1.6 m） | 淹没路段 → 通行阻断、抢险路径 |
| 11 | 20-承灾体 | [`seg.road_debris_aerial`](../docs/20-承灾体/seg.road_debris_aerial.md) | ★★ | C（0.03 m 航拍） | 航拍道路阻断精细判定 |
| 12 | 20-承灾体 | [`seg.road_intact_aerial`](../docs/20-承灾体/seg.road_intact_aerial.md) | ★ | C（0.03 m 航拍） | 同上，做对照 |
| 13 | 20-承灾体 | [`seg.storage_tank`](../docs/20-承灾体/seg.storage_tank.md) | ★ | B（0.5–1 m） | 洪水次生风险源（危化品） |
| 14 | 20-承灾体 | [`seg.vehicle_trapped_aerial`](../docs/20-承灾体/seg.vehicle_trapped_aerial.md) | ★★ | C（0.03 m 航拍） | 应急救援：受困目标 |
| 15 | 70-制图与报告 | [`model.summarize`](../docs/70-制图与报告/model.summarize.md) | ★★★ | B（换 LLM 端点） | 值班简报文字；需 API Key，数据出境需评估 |
| 16 | 70-制图与报告 | [`report.extract_evidence`](../docs/70-制图与报告/report.extract_evidence.md) | ★★ | A | 多步结果的自动汇总，不调模型 |
| 17 | 70-制图与报告 | [`vis.add_map_elements`](../docs/70-制图与报告/vis.add_map_elements.md) | ★★★ | A | 成品图规范化 |
| 18 | 70-制图与报告 | [`vis.bar_chart`](../docs/70-制图与报告/vis.bar_chart.md) | ★★ | A | 分区统计展示 |
| 19 | 70-制图与报告 | [`vis.before_after_panel`](../docs/70-制图与报告/vis.before_after_panel.md) | ★★★ | A | 汛前汛后对比 |
| 20 | 70-制图与报告 | [`vis.damage_map`](../docs/70-制图与报告/vis.damage_map.md) | ★★★ | A | 预警产品出图 |
| 21 | 70-制图与报告 | [`vis.heatmap`](../docs/70-制图与报告/vis.heatmap.md) | ★★ | A | 隐患点、报汛站、受灾点密度 |
| 22 | 70-制图与报告 | [`vis.line_chart`](../docs/70-制图与报告/vis.line_chart.md) | ★★ | A | 水位/面积过程线 |
| 23 | 70-制图与报告 | [`vis.overlay_mask`](../docs/70-制图与报告/vis.overlay_mask.md) | ★★★ | A | 淹没范围图 |
| 24 | 70-制图与报告 | [`vis.pie_chart`](../docs/70-制图与报告/vis.pie_chart.md) | ★★ | A | 构成占比 |
| 25 | 70-制图与报告 | [`vis.report_page`](../docs/70-制图与报告/vis.report_page.md) | ★★★ | A | 值班简报 |
| 26 | 70-制图与报告 | [`vis.route_map`](../docs/70-制图与报告/vis.route_map.md) | ★★ | A | 抢险路线图 |
| 27 | 70-制图与报告 | [`vis.temporal_panel`](../docs/70-制图与报告/vis.temporal_panel.md) | ★★★ | A | 水情/旱情演变序列（涨水—峰值—退水） |
| 28 | 60-计算与决策 | [`calc.add`](../docs/60-计算与决策/calc.add.md) | ★★ | A | 累计量 |
| 29 | 60-计算与决策 | [`calc.diff`](../docs/60-计算与决策/calc.diff.md) | ★★ | A | 偏差评估 |
| 30 | 60-计算与决策 | [`calc.div`](../docs/60-计算与决策/calc.div.md) | ★★ | A | 比例、变化率、单位换算 |
| 31 | 60-计算与决策 | [`calc.greater_than`](../docs/60-计算与决策/calc.greater_than.md) | ★★ | A | 超阈值判定 |
| 32 | 60-计算与决策 | [`calc.mul`](../docs/60-计算与决策/calc.mul.md) | ★★ | A | 面积×深度、权重×分值 |
| 33 | 60-计算与决策 | [`calc.point_distance`](../docs/60-计算与决策/calc.point_distance.md) | ★★ | A | 站点间距、影响半径 |
| 34 | 60-计算与决策 | [`calc.sub`](../docs/60-计算与决策/calc.sub.md) | ★★ | A | 变化量 |
| 35 | 60-计算与决策 | [`calc.volume`](../docs/60-计算与决策/calc.volume.md) | ★★ | A | 蓄水量、土方量、淹没水量 |
| 36 | 60-计算与决策 | [`calc.weighted_sum`](../docs/60-计算与决策/calc.weighted_sum.md) | ★★ | A | 综合旱情指数（降水+温度+土壤湿度加权） |
| 37 | 60-计算与决策 | [`logi.priority_score`](../docs/60-计算与决策/logi.priority_score.md) | ★★ | A | 受灾点优先级排序 |
| 38 | 60-计算与决策 | [`logi.resource_allocation`](../docs/60-计算与决策/logi.resource_allocation.md) | ★★ | A | 抢险队伍/物资分配 |
| 39 | 60-计算与决策 | [`logi.truck_trips`](../docs/60-计算与决策/logi.truck_trips.md) | ★★ | A | 物资/土方运输车次 |
| 40 | 60-计算与决策 | [`tool.chart_data`](../docs/60-计算与决策/tool.chart_data.md) | ★★ | A | 为柱/折线图准备数据 |
| 41 | 60-计算与决策 | [`tool.loop`](../docs/60-计算与决策/tool.loop.md) | ★★★ | A | 按网格/按行政区批量算，是「分区统计」的编排器 |
| 42 | 60-计算与决策 | [`tool.reduce`](../docs/60-计算与决策/tool.reduce.md) | ★★★ | A | 找极值网格（最热/最深/最旱） |
| 43 | 90-其他感知 | [`seg.lava`](../docs/90-其他感知/seg.lava.md) | ○ | D（业务无关） | 火山专用 |
| 44 | 90-其他感知 | [`seg.plane`](../docs/90-其他感知/seg.plane.md) | ○ | D（业务无关） | 无关 |
| 45 | 90-其他感知 | [`seg.playground`](../docs/90-其他感知/seg.playground.md) | ○ | D（业务无关） | 仅在「避难场所选址」这类派生任务中有用 |
| 46 | 90-其他感知 | [`seg.pool_aerial`](../docs/90-其他感知/seg.pool_aerial.md) | ○ | D（业务无关） | 无关 |
| 47 | 90-其他感知 | [`seg.roundabout`](../docs/90-其他感知/seg.roundabout.md) | ○ | D（业务无关） | 无关 |
| 48 | 90-其他感知 | [`seg.ship`](../docs/90-其他感知/seg.ship.md) | ○ | D（业务无关） | 内河航运场景可微调后使用 |
| 49 | 90-其他感知 | [`seg.swimming_pool`](../docs/90-其他感知/seg.swimming_pool.md) | ○ | D（业务无关） | 无关 |
| 50 | 90-其他感知 | [`seg.tree_fallen_aerial`](../docs/90-其他感知/seg.tree_fallen_aerial.md) | ★ | C（0.03 m 航拍） | 台风/洪涝伴生，河道行洪障碍 |
| 51 | 90-其他感知 | [`seg.tree_standing_aerial`](../docs/90-其他感知/seg.tree_standing_aerial.md) | ○ | D（业务无关） | 对照类别 |
| 52 | 90-其他感知 | [`seg.vehicle`](../docs/90-其他感知/seg.vehicle.md) | ○ | D（业务无关） | 与灾情关联弱 |
| 53 | 90-其他感知 | [`seg.vehicle_free_aerial`](../docs/90-其他感知/seg.vehicle_free_aerial.md) | ○ | D（业务无关） | 对照类别 |
| 54 | 80-POI-点位 | [`poi.damage_population_exposure`](../docs/80-POI-点位/poi.damage_population_exposure.md) | ★★ | A | 受影响人口优先序 |
| 55 | 80-POI-点位 | [`poi.filter_by_attribute`](../docs/80-POI-点位/poi.filter_by_attribute.md) | ★★ | A | 只看医院/学校/水厂 |
| 56 | 80-POI-点位 | [`poi.filter_by_damage`](../docs/80-POI-点位/poi.filter_by_damage.md) | ★★ | A | 学校/医院受淹排查 |
| 57 | 80-POI-点位 | [`poi.filter_by_intact`](../docs/80-POI-点位/poi.filter_by_intact.md) | ★ | A | 可用资源点 |
| 58 | 80-POI-点位 | [`poi.group_by`](../docs/80-POI-点位/poi.group_by.md) | ★★ | A | 按行政区/地类汇总 |
| 59 | 80-POI-点位 | [`poi.search_by_name`](../docs/80-POI-点位/poi.search_by_name.md) | ★ | A | 按地名定位 |
| 60 | 80-POI-点位 | [`poi.to_vector`](../docs/80-POI-点位/poi.to_vector.md) | ★★ | A | POI 数据入库 |
| 61 | 80-POI-点位 | [`poi.world_to_pixel`](../docs/80-POI-点位/poi.world_to_pixel.md) | ★★ | A | 把业务点位对齐到卫星影像 |
| 62 | 40-栅格分析 | [`mask.compose_multiclass`](../docs/40-栅格分析/mask.compose_multiclass.md) | ★★ | A | 把「常水体/新增水体/退水」合成一张图 |
| 63 | 40-栅格分析 | [`ras.area`](../docs/40-栅格分析/ras.area.md) | ★★★ | A | 淹没面积、受旱面积、水域面积 |
| 64 | 40-栅格分析 | [`ras.clip`](../docs/40-栅格分析/ras.clip.md) | ★★ | A | 按流域/行政区裁切 |
| 65 | 40-栅格分析 | [`ras.concat`](../docs/40-栅格分析/ras.concat.md) | ★★★ | A | 构造 14 波段输入（多光谱 + DEM + 坡度）的必经步骤 |
| 66 | 40-栅格分析 | [`ras.count_pixels`](../docs/40-栅格分析/ras.count_pixels.md) | ★★ | A | 面积前的中间量 |
| 67 | 40-栅格分析 | [`ras.diff`](../docs/40-栅格分析/ras.diff.md) | ★★★ | A | 多期差值、DSM−DEM 求相对高度 |
| 68 | 40-栅格分析 | [`ras.focal_stats`](../docs/40-栅格分析/ras.focal_stats.md) | ★★★ | A | 热点检测、平滑、DEM 局部粗糙度 |
| 69 | 40-栅格分析 | [`ras.grid_windows`](../docs/40-栅格分析/ras.grid_windows.md) | ★★★ | A | 面雨量/旱情分区统计的基础 |
| 70 | 40-栅格分析 | [`ras.reproject`](../docs/40-栅格分析/ras.reproject.md) | ★★★ | A | 多源数据统一坐标系（国产影像常为 CGCS2000） |
| 71 | 40-栅格分析 | [`ras.resample`](../docs/40-栅格分析/ras.resample.md) | ★★★ | A | 统一 GSD：模型对分辨率敏感，这一步不能省 |
| 72 | 40-栅格分析 | [`ras.sample_point`](../docs/40-栅格分析/ras.sample_point.md) | ★★ | A | 站点/断面取值 |
| 73 | 40-栅格分析 | [`ras.sample_points`](../docs/40-栅格分析/ras.sample_points.md) | ★★ | A | 水文站点批量采样 |
| 74 | 40-栅格分析 | [`ras.stats`](../docs/40-栅格分析/ras.stats.md) | ★★★ | A | 水位/温度/降水量的区域统计 |
| 75 | 40-栅格分析 | [`ras.threshold`](../docs/40-栅格分析/ras.threshold.md) | ★★★ | A | 最通用的一招：LST/NDVI/水深/降水栅格都能阈值化 |
| 76 | 40-栅格分析 | [`ras.vectorize`](../docs/40-栅格分析/ras.vectorize.md) | ★★★ | A | 淹没范围出图、与行政区叠加的前提 |
| 77 | 30-地形与地表变化 | [`ras.contour`](../docs/30-地形与地表变化/ras.contour.md) ★ | ★★ | A | 等高线出图、坡度分级底图 |
| 78 | 30-地形与地表变化 | [`ras.flow`](../docs/30-地形与地表变化/ras.flow.md) ★ | ★★★ | A | 填洼→流向→汇流，流域提取与洪水演进的前置 |
| 79 | 30-地形与地表变化 | [`ras.hillshade`](../docs/30-地形与地表变化/ras.hillshade.md) | ★★★ | A | 地形地貌可视化、滑坡/泥石流易发性底图 |
| 80 | 30-地形与地表变化 | [`ras.slope`](../docs/30-地形与地表变化/ras.slope.md) | ★★★ | A | 坡度是滑坡模型与汇流分析的基础因子 |
| 81 | 30-地形与地表变化 | [`ras.terrain`](../docs/30-地形与地表变化/ras.terrain.md) ★ | ★★★ | A | 一次出坡度/坡向/曲率/TRI/TPI/粗糙度，地形地貌分析的地基 |
| 82 | 30-地形与地表变化 | [`seg.landslide_bitemporal`](../docs/30-地形与地表变化/seg.landslide_bitemporal.md) | ★★★ | B（未实测） | 无 DEM 时的替代路径 |
| 83 | 30-地形与地表变化 | [`seg.landslide_ms`](../docs/30-地形与地表变化/seg.landslide_ms.md) | ★★★ | C（14 波段归一化） | 地形地貌变化主力；必须 14 波段 |
| 84 | 30-地形与地表变化 | [`seg.vegetation`](../docs/30-地形与地表变化/seg.vegetation.md) | ★★★ | B（仅单期） | 旱情：植被覆盖变化、受旱耕地识别 |
| 85 | 50-矢量与空间关系 | [`vec.buffer`](../docs/50-矢量与空间关系/vec.buffer.md) | ★★★ | A | 河道缓冲带、溃堤影响带、河岸带 |
| 86 | 50-矢量与空间关系 | [`vec.build_graph`](../docs/50-矢量与空间关系/vec.build_graph.md) | ★★ | A | 通行能力建模 |
| 87 | 50-矢量与空间关系 | [`vec.centroid`](../docs/50-矢量与空间关系/vec.centroid.md) | ★★ | A | 灾情中心点 |
| 88 | 50-矢量与空间关系 | [`vec.clip`](../docs/50-矢量与空间关系/vec.clip.md) | ★★ | A | 裁到流域/行政区边界 |
| 89 | 50-矢量与空间关系 | [`vec.connected_components`](../docs/50-矢量与空间关系/vec.connected_components.md) | ★★ | A | 数淹没片数、损毁建筑栋数 |
| 90 | 50-矢量与空间关系 | [`vec.convex_hull`](../docs/50-矢量与空间关系/vec.convex_hull.md) | ★★ | A | 灾害影响范围包络 |
| 91 | 50-矢量与空间关系 | [`vec.dissolve`](../docs/50-矢量与空间关系/vec.dissolve.md) | ★★★ | A | 把破碎淹没斑块合成连片淹没区 |
| 92 | 50-矢量与空间关系 | [`vec.filter_by_area`](../docs/50-矢量与空间关系/vec.filter_by_area.md) | ★★★ | A | 去掉掩膜噪点，几乎每步都用 |
| 93 | 50-矢量与空间关系 | [`vec.filter_by_attribute`](../docs/50-矢量与空间关系/vec.filter_by_attribute.md) | ★★ | A | 按地类/行政区代码筛选 |
| 94 | 50-矢量与空间关系 | [`vec.filter_by_distance`](../docs/50-矢量与空间关系/vec.filter_by_distance.md) | ★★ | A | 以水库/险工段为中心的影响范围筛选 |
| 95 | 50-矢量与空间关系 | [`vec.graph_shortest_path`](../docs/50-矢量与空间关系/vec.graph_shortest_path.md) | ★★ | A | 抢险/撤离路径规划 |
| 96 | 50-矢量与空间关系 | [`vec.intersect`](../docs/50-矢量与空间关系/vec.intersect.md) | ★★★ | A | 淹没范围 ∩ 耕地/居民地/行政区 |
| 97 | 50-矢量与空间关系 | [`vec.kbuffer`](../docs/50-矢量与空间关系/vec.kbuffer.md) | ★★ | A | 分级影响区（100/500/1000 m） |
| 98 | 50-矢量与空间关系 | [`vec.length`](../docs/50-矢量与空间关系/vec.length.md) | ★★ | A | 河道长度、道路淹没长度 |
| 99 | 50-矢量与空间关系 | [`vec.max_polygon`](../docs/50-矢量与空间关系/vec.max_polygon.md) | ★★ | A | 找主淹没区/最大灾区 |
| 100 | 50-矢量与空间关系 | [`vec.nearest`](../docs/50-矢量与空间关系/vec.nearest.md) | ★★ | A | 受灾点最近的安置点/物资库 |
| 101 | 50-矢量与空间关系 | [`vec.perimeter`](../docs/50-矢量与空间关系/vec.perimeter.md) | ★★ | A | 水域岸线长度 |
| 102 | 50-矢量与空间关系 | [`vec.pixel_to_world`](../docs/50-矢量与空间关系/vec.pixel_to_world.md) | ★★ | A | 把图上位置转成可上报的坐标 |
| 103 | 50-矢量与空间关系 | [`vec.point_in_polygon`](../docs/50-矢量与空间关系/vec.point_in_polygon.md) | ★★★ | A | 站点/村庄是否位于淹没区或风险区 |
| 104 | 50-矢量与空间关系 | [`vec.raster_stats`](../docs/50-矢量与空间关系/vec.raster_stats.md) | ★★★ | A | 流域内平均降水、行政区平均 LST、耕地平均 NDVI |
| 105 | 50-矢量与空间关系 | [`vec.repair_min_edges`](../docs/50-矢量与空间关系/vec.repair_min_edges.md) | ★★ | A | 断路情况下最小抢通方案 |
| 106 | 50-矢量与空间关系 | [`vec.road_centerline_extraction`](../docs/50-矢量与空间关系/vec.road_centerline_extraction.md) | ★★ | A | 路网骨架，用于通行分析 |
| 107 | 50-矢量与空间关系 | [`vec.simplify`](../docs/50-矢量与空间关系/vec.simplify.md) | ★★ | A | 矢量过大时压缩，便于发布 |
| 108 | 50-矢量与空间关系 | [`vec.voronoi`](../docs/50-矢量与空间关系/vec.voronoi.md) | ★ | A | 物资投放点/水文站服务范围 |
| 109 | 10-水体与淹没 | [`seg.flood`](../docs/10-水体与淹没/seg.flood.md) | ★★★ | C（跨分辨率失效） | 洪水淹没范围主入口；两次水体推理再相减 |
| 110 | 10-水体与淹没 | [`seg.reservoir`](../docs/10-水体与淹没/seg.reservoir.md) | ★★★ | C（14 波段归一化） | 干旱核心：水域面积萎缩监测；需 14 波段输入 |
| 111 | 10-水体与淹没 | [`seg.water_aerial`](../docs/10-水体与淹没/seg.water_aerial.md) | ★★★ | C（0.03 m 航拍） | 应急航拍精细淹没边界 |
