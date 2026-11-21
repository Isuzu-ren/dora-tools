# 50-矢量与空间关系

24 件，全库最大的一域，全部无权重。按用途分三组：

- **叠加与筛选**：`vec.intersect`、`vec.buffer`、`vec.clip`、`vec.filter_by_*`
- **几何后处理**：`vec.dissolve`、`vec.simplify`、`vec.centroid`、`vec.convex_hull`、`vec.max_polygon`
- **路网**：`vec.road_centerline_extraction` → `vec.build_graph` → `vec.graph_shortest_path`，
  外加 `vec.repair_min_edges`（最少抢通路段）

预警平台里被调用最频繁的是 `vec.raster_stats`（分区统计）：把栅格按行政区/流域/灌区汇总，
「XX 县平均降雨多少、多少亩受旱」这类问法绝大多数由它一件支撑。

## 工具速查（24 件）

| 工具 | 相关性 | 可迁移性 | 用途 |
|---|---|---|---|
| [`vec.buffer`](vec.buffer.md) | ★★★ | A | 河道缓冲带、溃堤影响带、河岸带 |
| [`vec.dissolve`](vec.dissolve.md) | ★★★ | A | 把破碎淹没斑块合成连片淹没区 |
| [`vec.filter_by_area`](vec.filter_by_area.md) | ★★★ | A | 去掉掩膜噪点，几乎每步都用 |
| [`vec.intersect`](vec.intersect.md) | ★★★ | A | 淹没范围 ∩ 耕地/居民地/行政区 |
| [`vec.point_in_polygon`](vec.point_in_polygon.md) | ★★★ | A | 站点/村庄是否位于淹没区或风险区 |
| [`vec.raster_stats`](vec.raster_stats.md) | ★★★ | A | 流域内平均降水、行政区平均 LST、耕地平均 NDVI |
| [`vec.build_graph`](vec.build_graph.md) | ★★ | A | 通行能力建模 |
| [`vec.centroid`](vec.centroid.md) | ★★ | A | 灾情中心点 |
| [`vec.clip`](vec.clip.md) | ★★ | A | 裁到流域/行政区边界 |
| [`vec.connected_components`](vec.connected_components.md) | ★★ | A | 数淹没片数、损毁建筑栋数 |
| [`vec.convex_hull`](vec.convex_hull.md) | ★★ | A | 灾害影响范围包络 |
| [`vec.filter_by_attribute`](vec.filter_by_attribute.md) | ★★ | A | 按地类/行政区代码筛选 |
| [`vec.filter_by_distance`](vec.filter_by_distance.md) | ★★ | A | 以水库/险工段为中心的影响范围筛选 |
| [`vec.graph_shortest_path`](vec.graph_shortest_path.md) | ★★ | A | 抢险/撤离路径规划 |
| [`vec.kbuffer`](vec.kbuffer.md) | ★★ | A | 分级影响区（100/500/1000 m） |
| [`vec.length`](vec.length.md) | ★★ | A | 河道长度、道路淹没长度 |
| [`vec.max_polygon`](vec.max_polygon.md) | ★★ | A | 找主淹没区/最大灾区 |
| [`vec.nearest`](vec.nearest.md) | ★★ | A | 受灾点最近的安置点/物资库 |
| [`vec.perimeter`](vec.perimeter.md) | ★★ | A | 水域岸线长度 |
| [`vec.pixel_to_world`](vec.pixel_to_world.md) | ★★ | A | 把图上位置转成可上报的坐标 |
| [`vec.repair_min_edges`](vec.repair_min_edges.md) | ★★ | A | 断路情况下最小抢通方案 |
| [`vec.road_centerline_extraction`](vec.road_centerline_extraction.md) | ★★ | A | 路网骨架，用于通行分析 |
| [`vec.simplify`](vec.simplify.md) | ★★ | A | 矢量过大时压缩，便于发布 |
| [`vec.voronoi`](vec.voronoi.md) | ★ | A | 物资投放点/水文站服务范围 |

## 相关但不在本域

- `ras.vectorize`（40-栅格分析）：掩膜转矢量是多数矢量流程的入口
- `poi.*`（80-POI-点位）：点位落进面内
- `vis.route_map`（70）：把路径画到底图上

## 列的含义

- **相关性**：★★★ 业务直接调用 / ★★ 流程必需 / ★ 特定子场景 / ○ 无交集
- **可迁移性**：A 零改造直迁 / B 加规范可用 / C 必须重训 / D 不建议迁
- 判定依据见 [`01-工具全景`](../01-工具全景.md) 与 [`99-附录/A-接入红线`](../99-附录/A-接入红线.md)
