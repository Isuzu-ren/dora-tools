# -*- coding: utf-8 -*-
"""文档内容层：领域导语、逐工具补充说明、参数释义、附录正文。

build_docs.py 只负责渲染，文案集中在这里，便于后续修订。
"""

# ---------------------------------------------------------------- 领域
DOMAINS = [
    ("water", "10-水体与淹没"),
    ("asset", "20-承灾体"),
    ("terrain", "30-地形与地表变化"),
    ("raster", "40-栅格分析"),
    ("vector", "50-矢量与空间关系"),
    ("compute", "60-计算与决策"),
    ("carto", "70-制图与报告"),
    ("poi", "80-POI-点位"),
    ("other", "90-其他感知"),
]

DOMAIN_INTRO = {
    "water": """本域只有 3 件，但都是水旱业务的主指标：淹没范围、水域面积、应急航拍水体。
三件全部依赖模型权重，且全部落在 B/C 档——这正是「业务主干需要改造或重训」的直接体现。

配套的能力不在这里：洪水面积与水量在栅格分析 / 计算与决策域（`ras.threshold`、`ras.area`、
`calc.volume`），其中 `ras.threshold` 做 SAR 后向散射阈值，是不需要任何权重的下限基线（IoU 0.267）。""",

    "asset": """14 件，覆盖建筑、道路、桥梁、车辆、储罐、港口与重建进度，是全库最「重」的一域：
全部依赖 1.31 GB 级的 BitemporalDPT 权重，全部要求灾前 + 灾后配对，全部要求 0.5–1.6 m。

建筑损毁与道路损毁是仅有的两个做过尺度敏感性实测的模型：1.6 m 可用（逐类 IoU 0.43–0.52）、
2.0 m 只能出总量（道路「阻断」只剩 0.23）、3.2 m 中间档塌陷。做灾损统计时请先读
`seg.building_damage` 页的「适用边界」。""",

    "terrain": """5 件：3 个模型（两个滑坡、一个植被）+ 2 个 DEM 派生（坡度、山体阴影）。

地形变化这条需求由本域加栅格分析的 `ras.diff` 共同闭环：两期 DEM 相减得高程变化（填挖、淤积、冲刷），
单期 DEM 出坡度与起伏形态，再叠加双时相滑坡模型得图斑。缺的是河道断面/冲淤量这类水文地貌算子，
以及水下地形。""",

    "raster": """15 件，全部无权重，是全库复用价值最高、迁移成本最低的一组：面积、统计、阈值、裁剪、
拼接、重采样、重投影、矢量化都在这里。

上线时「从掩膜到结论」这条尾巴——面积换算、分区统计、投影统一、出图前的矢量化——主要由本域
加矢量域承担。注意 `ras.diff` 与 `ras.focal_stats` 虽常用于地形，但对任意栅格通用，因此归在本域。""",

    "vector": """24 件，全库最大的一域，全部无权重。按用途分三组：

- **叠加与筛选**：`vec.intersect`、`vec.buffer`、`vec.clip`、`vec.filter_by_*`
- **几何后处理**：`vec.dissolve`、`vec.simplify`、`vec.centroid`、`vec.convex_hull`、`vec.max_polygon`
- **路网**：`vec.road_centerline_extraction` → `vec.build_graph` → `vec.graph_shortest_path`，
  外加 `vec.repair_min_edges`（最少抢通路段）

预警平台里被调用最频繁的是 `vec.raster_stats`（分区统计）：把栅格按行政区/流域/灌区汇总，
「XX 县平均降雨多少、多少亩受旱」这类问法绝大多数由它一件支撑。""",

    "compute": """15 件：纯标量运算 + 决策规则 + 两个编排器。本域不碰空间数据，但决定「算出来的数怎么用」：
面积乘深度得蓄水量、多指标加权得综合旱情指数、按需求比例分配队伍与物资。

`tool.loop` 是这一域的中心：它把「一条链」变成「一个可并行的批处理」，`bind` 能把循环项注入下游参数。
没有它，Agent 只能逐条手写调用，步数会翻几倍。""",

    "carto": """13 件 = 11 件制图 + 2 件汇总（证据抽取、LLM 摘要）。

预警平台的最后一公里不是数字，是一张能发出去的图：`vis.damage_map` 出专题图，
`vis.temporal_panel` 出涨水—峰值—退水序列，`vis.report_page` 出一页式值班简报。
除 `model.summarize` 需要 LLM 接口外，其余全部无权重。""",

    "poi": """8 件，点位数据与灾害的交叉。输入是 GeoJSON 点（学校、医院、水厂、安置点），
输出是「哪些点落进了受损建筑或淹没区、涉及多少人口、按什么优先级处置」。依赖 geopandas，无权重。

这一域的价值在于把「空间范围」翻译成「人和设施」——指挥决策关心的是后者。""",

    "other": """11 件，与本项目基本无关：火山熔岩、飞机、船舶、泳池、操场、环岛、车辆计数，
以及 1 件弱相关（倒伏树木，用于河道行洪障碍排查）。

保留是为了台账完整（108 这个数字要与上游一致）。**每页页首都标注了与本项目的关系**。
另外：其中 10 件共用 `seg_aerial` 与 `seg_isaid` 两份权重，删工具省不出存储。
""",
}

# ---------------------------------------------------------------- 域级统一口径
# 模型密集型域把「输入域 / 时相 / 是否实测 / 可用结论」收在一张表里，避免 14 页各写一遍。
DOMAIN_TABLES = {
    "asset": """## 实测口径

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
> 结论方向可靠，但"落在可用还是不可用的边界上"没被验证过。""",

    "water": """## 实测口径

本域 3 件都是主指标，但可迁移性全是 B/C——业务主干恰好落在需要改造或重训的档位上。

| 工具 | 输入域 | 时相 | 实测 | 可用结论 |
|---|---|---|---|---|
| `seg.flood` | 光学 3 波段；训练 0.5–1 m | **灾前 + 灾后** | **是**（C2：83 景） | 10 m 输入 IoU 0.107、65% 零检出；输出掩膜是 PNG、**无地理参考** |
| `seg.reservoir` | 14 波段（S2 12 + 坡度 + DEM），10 m | 单期 | 否（契约推定） | 波段顺序错**不报错**，面积可差 81%；换 GF 系列需重标定 |
| `seg.water_aerial` | 无人机 0.03 m | 单期 | 否 | 星载影像上目标尺度不符，不可用 |

短期替代：淹没范围先用 `ras.threshold` 做 SAR −16 dB（IoU 0.267，零权重）顶着，
水域面积用 `ras.threshold` + `ras.area` 粗算，并标注「趋势可用、绝对值待校准」。""",

    "terrain": """## 实测口径

5 件里 3 件是模型、2 件是纯算法，边界完全不同，别混着看。

| 工具 | 输入域 | 时相 | 实测 | 可用结论 |
|---|---|---|---|---|
| `seg.landslide_ms` | 14 波段（S2 12 + 坡度 + DEM），10 m | 单期 | **是**（C1：245 景） | 域内 IoU 0.262，**这是上界不是泛化**；波段数不对会抛错 |
| `seg.landslide_bitemporal` | 3 波段，0.59 m | 双期 | 否 | 不需要 DEM，是没有地形数据时的替代路径 |
| `seg.vegetation` | 3 波段，0.5–1 m | **仅单期** | **是**（C3.3 / C4） | 两期相减平均变化 37.4%，会把模型漂移当灾损；输出是 0/255 |
| `ras.slope` | DEM 单波段 | 单期 | — | 纯算法，Horn 1981，结果只取决于输入数值 |
| `ras.hillshade` | DEM 单波段 | 单期 | — | 纯算法，纯可视化用途 |

地形变化要闭环，还差一步两期 DEM 相减——用 `ras.diff`（在 40-栅格分析域）。""",
}

# ---------------------------------------------------------------- 参数释义
PARAM_HINTS = {
    "image_path": "输入栅格路径（GeoTIFF / PNG；PNG 无地理参考）",
    "pre_image_path": "灾前影像路径",
    "post_image_path": "灾后影像路径",
    "image_a_path": "栅格 A 路径",
    "image_b_path": "栅格 B 路径",
    "mask_path": "掩膜路径（二值或多类）",
    "vector_path": "矢量路径（GeoJSON）",
    "vector_a_path": "矢量层 A（GeoJSON）",
    "vector_b_path": "矢量层 B（GeoJSON）",
    "output_path": "输出文件路径",
    "dst_path": "目标文件路径",
    "dem_path": "DEM 路径",
    "path": "文件路径",
    "threshold": "阈值",
    "op": "比较运算符：`>=` `>` `<=` `<` `==`",
    "band": "波段号，从 1 开始",
    "band_a": "A 使用的波段号",
    "band_b": "B 使用的波段号",
    "true_value": "命中像元写入的值",
    "false_value": "未命中像元写入的值",
    "pixel_size_m": "像元边长（米）。掩膜无地理参考时必须显式给出",
    "classes": "要保留的类别值列表",
    "class_values": "类别值到名称的映射",
    "units": "单位：`degrees` 或 `percent`",
    "azimuth": "光源方位角（度）",
    "altitude": "光源高度角（度）",
    "z_factor": "高程夸张系数",
    "statistic": "统计量：mean / max / min / std / median",
    "window_size": "邻域窗口边长（像元）",
    "target_gsd": "目标分辨率（米）",
    "resampling": "重采样方法：nearest / bilinear / cubic",
    "crs": "目标坐标系（EPSG 代码或 WKT）",
    "distance_m": "距离阈值（米）",
    "min_area_m2": "面积阈值（平方米）",
    "attribute": "属性字段名",
    "value": "属性取值",
    "operator": "比较运算符",
    "top_k": "取前 k 个",
    "n": "数量或网格边长",
    "grid_size": "网格边长（格数）",
    "image_list": "影像路径列表",
    "values": "待归约的数值列表",
    "field": "参与运算的字段名",
    "mode": "归约方式：max / min / mean / sum",
    "calls": "要循环执行的工具调用列表",
    "loop_over": "循环遍历的列表（与 calls 配合）",
    "bind": "把循环项绑定到下游参数名",
    "question": "问题文本",
    "text": "文本内容",
    "points": "点要素列表",
    "lon": "经度",
    "lat": "纬度",
    "title": "图标题",
    "labels": "标签列表",
    "x": "横轴数值或标签",
    "y": "纵轴数值",
    "names": "名称列表",
    "sizes": "尺寸列表",
    "colors": "颜色列表",
    "legend": "是否绘制图例",
    "stats": "统计数据字典",
    "tables": "表格数据",
    "images": "影像路径列表",
    "before_image_path": "变化前影像",
    "after_image_path": "变化后影像",
    "route": "路径（点序列或线要素）",
    "features": "要素列表",
    "population_field": "人口数字段",
    "damage_field": "损毁状态字段",
    "group_field": "分组字段",
    "class_field": "类别字段",
    "kernel": "卷积/邻域核尺寸",
    "sigma": "高斯核标准差",
    "factor": "缩放系数",
    "scale": "缩放倍数",
    "width": "宽度（像元）",
    "height": "高度（像元）",
    "x0": "左上角列号",
    "y0": "左上角行号",
    "x1": "右下角列号",
    "y1": "右下角行号",
    "size": "尺寸",
    "tile_size": "瓦片边长",
    "max_distance_m": "最大搜索距离（米）",
    "k": "邻居数量",
    "radius_m": "半径（米）",
    "buffer_m": "缓冲距离（米）",
    "level": "缓冲级别",
    "top_n": "取前 n 项",
    "score_field": "分数字段",
    "weight": "权重",
    "weights": "权重字典",
    "capacity": "单车容量",
    "total": "总量",
    "budget": "预算或总量",
    "priority": "优先级列表",
    "supply": "供给量",
    "demand": "需求量",
    "out_path": "输出文件路径",
    "data": "输入数据（数组或字典，结构见源码）",
    "raster_path": "栅格路径",
    "a": "参与运算的数值或栅格 A",
    "b": "参与运算的数值或栅格 B",
    "trajectory": "工具调用轨迹（列表，每项含工具名与参数）",
    "base_image_path": "底图影像路径",
    "class_labels": "类别值到名称的映射，用于图例",
    "alpha": "叠加透明度（0–1）",
    "points_path": "点要素文件（GeoJSON）",
    "geojson_path": "GeoJSON 文件路径",
    "image_paths": "影像路径列表",
    "overlay_mask_path": "叠加掩膜路径",
    "attribute_name": "属性字段名",
    "allowed_values": "允许的取值列表",
    "name": "名称",
    "exact": "是否精确匹配",
    "graph_path": "路网图文件路径",
    "topk": "取前 k 个",
    "task_question": "任务问题文本",
    "final_answer_template": "最终答案模板",
    "model": "模型名称",
    "include_empty_masks": "是否保留空掩膜",
    "target_classes": "目标类别值列表",
    "legend_items": "图例条目",
    "legend_alpha": "图例透明度",
    "point_markers": "点标记样式",
    "north_arrow": "是否绘制指北针",
    "scale_bar": "是否绘制比例尺",
    "bandwidth": "核密度带宽",
    "colormap": "色带名称",
    "map_image_path": "地图影像路径",
    "chart_image_path": "图表影像路径",
    "summary_text": "摘要文字",
    "key_statistics": "关键统计（字典）",
    "path_pixels": "路径的像素坐标列表",
    "start_point": "起点",
    "end_point": "终点",
    "route_color": "路径颜色",
    "route_width": "路径线宽",
}


# ---------------------------------------------------------------- 逐工具补充
# 只写「评测结论 / 已知坑 / 上下游」这类源码里没有的信息。
NOTES = {
    "seg.flood": {
        "boundary": "需要**灾前 + 灾后同一区域的两期影像**；只给单期时无法调用。水体权重在 10 m 输入上 IoU 0.107、83 景中 54 景零检出（训练于 0.5–1 m）。",
        "pitfall": "内部两次 `_water_mask` 调用**不传参考栅格**，所以输出掩膜是 PNG、没有地理参考——下游算面积必须手动给 `pixel_size_m`。",
        "tip": "灾前若处于枯水期，河滩与水库消落带会被判成「新增淹没」；反过来用（丰水期→枯水期）可算退水面积，那是旱情指标。",
        "related": ["seg.reservoir", "ras.threshold", "ras.area"],
    },
    "seg.reservoir": {
        "boundary": "必须 **14 波段且顺序固定**（B1–B12 + 坡度 + DEM），并带 Landslide4Sense 的归一化常量；换 GF 系列需重标定或重训。",
        "pitfall": "波段对调**不报错**：DEM 与坡度互换后，同一景面积从 0.815 km² 变成 1.476 km²。",
        "related": ["ras.concat", "ras.resample", "ras.area"],
    },
    "seg.water_aerial": {
        "boundary": "0.03 m 航拍专用，星载影像上目标尺度不符。有航次时它是最精细的边界来源。",
        "related": ["vis.overlay_mask", "ras.area"],
    },
    "seg.building_damage": {
        "boundary": "训练于 0.8 m；1.6 m 逐类 IoU 0.43–0.52、2.0 m 只能出「是否损毁」总量、3.2 m 中间档塌陷。",
        "pitfall": "**16 位值域直接喂入会整幅全背景**（5 景中 4 景全空、1 景剩 281 px），且不报错。输入必须先拉回 0–255。",
        "tip": "输出 0=背景、1=完好、2=部分损毁、3=完全损毁。大图会走 out-of-core；16 MP 以上建议自己先切片。",
        "related": ["seg.road_damage", "ras.resample", "vec.intersect"],
    },
    "seg.building_damage_opt_sar": {
        "boundary": "灾后必须是 SAR，且需先在工具外完成辐射定标、地理编码、斑点滤波。精度未实测（本地无真值）。",
        "tip": "中国汛期主雨带云量高，光学连续多日不可用；这件是为那个场景准备的。",
        "related": ["seg.building_damage", "ras.area"],
    },
    "seg.road_damage": {
        "boundary": "0.5–1 m 训练。2.0 m 时「阻断」面积只剩 0.23、逐类 IoU 0.193，**阻断结论不可用**；建议 ≤1.6 m 并人工复核。",
        "related": ["vec.road_centerline_extraction", "vec.build_graph"],
    },
    "seg.building_lowres": {
        "boundary": "3.46 m 专用（PlanetScope 一类），用于大范围承灾体底数。**71.2 s/MP**，512² 需约 5.5 GB 内存，16 MP 以上会 OOM。",
        "related": ["ras.resample", "vec.intersect"],
    },
    "seg.vegetation": {
        "boundary": "**只做单期**。两期相减的平均面积变化 37.4%、一致率低至 0.63，会把模型漂移当成灾损变化。",
        "pitfall": "文档说取第 5/6 类，实际输出是 **0/255 二值掩膜**（`_binary_mask` 的合并结果），统计时按「>0」计数。",
        "related": ["ras.area", "vis.temporal_panel"],
    },
    "seg.landslide_ms": {
        "boundary": "域内 IoU 0.262（Landslide4Sense 就是它的训练域），**这是上界不是泛化**。10 m 输入、14 波段。",
        "pitfall": "波段数不对会**抛错**（这是好事）；但 DEM 与坡度对调不报错，只会悄悄变差。",
        "related": ["ras.concat", "ras.slope", "ras.diff"],
    },
    "seg.landslide_bitemporal": {
        "boundary": "0.59 m、双时相、3 波段，**不需要 DEM**——是没有 DEM 数据时的替代路径。精度未实测。",
        "related": ["seg.landslide_ms", "ras.diff"],
    },
    "ras.threshold": {
        "tip": "SAR 水体最实用的下限基线：VV < −16 dB 得 IoU 0.267，零权重、801 次调用零报错。任何新模型要先超过它。",
        "boundary": "只做单波段二值化，不能做波段比值（算不了 NDVI/NDWI，那是缺口）。",
        "related": ["ras.area", "ras.vectorize"],
    },
    "ras.area": {
        "tip": "面积 = 像元数 × 像元面积。若掩膜是 PNG（无地理参考），必须显式传 `pixel_size_m`，否则数字没有意义。",
        "related": ["ras.count_pixels", "ras.vectorize"],
    },
    "ras.resample": {
        "tip": "模型对分辨率敏感，接入前这一步不能省。降采样只改像素，不改类别语义——3.2 m 时「部分损毁」会塌得比「完全损毁」更快。",
        "related": ["ras.reproject", "seg.building_damage"],
    },
    "ras.concat": {
        "tip": "构造 14 波段输入的**唯一途径**。顺序必须是 B1–B12、坡度、DEM，错序不报错但结果偏移。",
        "related": ["seg.landslide_ms", "seg.reservoir"],
    },
    "ras.vectorize": {
        "tip": "输出多边形自带 `area_m2`；碎斑用 `vec.filter_by_area` 清，再 `vec.intersect` 叠行政区。",
        "related": ["vec.filter_by_area", "vec.intersect"],
    },
    "ras.diff": {
        "tip": "只做 A − B 的逐像元相减，**不能除**——所以算不了任何指数。DSM − DEM 求相对高度也用它。",
        "related": ["ras.threshold", "ras.area"],
    },
    "vec.raster_stats": {
        "tip": "唯一支持 `return_features=True` 逐要素返回的统计工具，可直接出表。「XX 县平均降雨」这类问法靠它一件支撑。",
        "related": ["ras.stats", "poi.group_by"],
    },
    "vec.build_graph": {
        "tip": "路网分析三步走：`road_centerline_extraction` → `build_graph` → `graph_shortest_path`。",
        "related": ["vec.road_centerline_extraction", "vec.graph_shortest_path"],
    },
    "vec.repair_min_edges": {
        "tip": "「最少抢通哪几段」——溃堤、断路场景下比最短路更贴近指挥决策。",
        "related": ["vec.build_graph"],
    },
    "tool.loop": {
        "tip": "把一条链变成批处理。实测：IF 模式把每轮平均工具步数从 6.9–9.5 降到 4.6，但分数没变——瓶颈在参数绑定，而 `bind` 正是它的解法。",
        "related": ["tool.reduce", "tool.chart_data"],
    },
    "tool.reduce": {
        "tip": "对 `tool.loop` 的结果做 max/min/mean，用来找极值网格（最热、最深、最旱）。",
        "related": ["tool.loop"],
    },
    "model.summarize": {
        "boundary": "需要外部 LLM Key；数据出境需评估，可换本地模型。输出是自然语言简报，不含数值校验。",
        "related": ["report.extract_evidence", "vis.report_page"],
    },
    "report.extract_evidence": {
        "tip": "**不调模型**，纯 numpy 从轨迹里抽结构化证据（各掩膜面积、时序），适合做多步结果的自动汇总。",
        "related": ["model.summarize", "tool.reduce"],
    },
    "vis.damage_map": {
        "tip": "标准专题图含图例、指北针、比例尺；掩膜先 `ras.vectorize` 再叠，边界更干净。",
        "related": ["vis.overlay_mask", "vis.add_map_elements"],
    },
    "vis.temporal_panel": {
        "tip": "吃一个影像列表，自动排布。水情/旱情的本质是「随时间怎么变」，这件正好对口。",
        "related": ["vis.before_after_panel", "ras.area"],
    },
    "poi.damage_population_exposure": {
        "tip": "把「范围」翻译成「人和设施」：损毁建筑内的 POI 按人口排序，直接给处置优先级。",
        "related": ["poi.filter_by_damage", "logi.priority_score"],
    },
}

# ---------------------------------------------------------------- 附录
APPENDIX_A = """# 附录 A · 接入红线

三条红线来自 C0–C5 实测，**不是建议，是前置校验**。写在文档里拦不住，要写进取数脚本。

```
① 分辨率 ≤1.6 m          否则中间档消失，灾损统计系统性低估
② 值域 0–255（uint8）    否则静默输出全背景
③ 切片边长取 518 整数倍   否则白付 4 倍算力
```

## 为什么是这三条

| 红线 | 实测依据 | 不遵守的后果 |
|---|---|---|
| 分辨率 ≤1.6 m | 1.6 m 逐类 IoU 0.43–0.52；2.0 m 道路「阻断」面积只剩 0.23；3.2 m 「部分损毁」塌到 0.35 而「完全损毁」还有 0.84 | 灾损统计系统性偏低，且偏向两极 |
| 值域 0–255 | 16 位物理量直接喂入：5 景中 4 景整幅全背景、1 景剩 281 px，**全程不报错** | 拿着一张全黑的图汇报「本地无灾情」 |
| 切片 518 整数倍 | 518² 用 4.56 s，512² 用 16.71 s（面积只差 2.3%） | 白付 3.66 倍算力 |

## 接入检查清单

- [ ] 影像 dtype 与值域已校验，必要时线性拉伸到 0–255
- [ ] 重采样到 ≤1.6 m（模型训练域 0.5–1 m 更好）
- [ ] 切片边长 518 的整数倍，且尺寸写进配置（同一景两次跑必须同参数）
- [ ] 波段顺序与模型契约一致（14 波段：B1–B12、坡度、DEM）
- [ ] 双时相模型有灾前 + 灾后配对，且两期几何已配准
- [ ] 掩膜带地理参考；若是 PNG，下游面积换算显式给像元大小
"""

APPENDIX_B = """# 附录 B · 已知陷阱

按「后果严重度」排序。**前四条最危险，因为它们不报错。**

| # | 现象 | 触发条件 | 后果 | 规避 |
|---|---|---|---|---|
| 1 | 16 位输入 → 整幅全背景 | 值域 0–65535 直输 | 看着像「没有灾情」 | 取数时校验 dtype/值域，转 0–255 |
| 2 | 波段顺序错 → 结果偏移 | 14 波段里 DEM 与坡度对调 | 面积 0.815 → 1.476 km²，不报错 | 固定波段顺序，写进接口契约 |
| 3 | 全零/损坏瓦片 → 空掩膜 | 云遮挡、取数失败留空片 | 该景被判「无目标」 | 上游校验非全零、非全常数 |
| 4 | 极小图静默通过 | 切片逻辑出错 | 无意义结果 | 校验最小尺寸 ≥64 |
| 5 | 3.2 m 输入 → 中间档消失 | 分辨率过粗 | 道路阻断 10/10 景归零 | 分辨率控制在 ≤1.6 m |
| 6 | 换窗口 → 面积差一两成 | 切片尺寸不固定 | 不可复现 | 固定瓦片尺寸（518 整数倍） |
| 7 | 16 MP 以上爆内存 | `seg.landslide_ms` / `seg.building_lowres` | OOM | 自己在外面切片 |
| 8 | 光学水体模型用于 10 m S2 | 跨分辨率 | IoU 0.107、召回 0.13 | 换 1 m 级数据或重训 |
| 9 | `seg.vegetation` 做两期对比 | 灾前灾后各跑一次 | 平均变化 37.4%，把漂移当灾损 | 只做单期 |
| 10 | `seg.flood` 用于单期影像 | 只有灾后一期 | 无法调用 | 补灾前影像 |

## 另外两件容易忽略的事

- **掩膜可能没有地理参考**：`_save_mask()` 只在参考栅格带 CRS 时才写 GeoTIFF；`seg.flood` 内部两次推理不传参考，所以它出的永远是 PNG。
- **错误处理不统一**：`poi.py` 全部有 `_tool_guard`，`analysis.py` 只有 25/41 件有；`calculate` / `vis` / `model` 没有统一包装。同一批工具，有的返回 `{"error": ...}`，有的直接抛异常。
"""

APPENDIX_C = """# 附录 C · 评测结论摘要

完整报告见主仓库 `my/DORA_工具效果与泛化评测报告.md`，全部数字来自 `outputs/eval_c5/facts.json`。

## 三个问题

| 问题 | 回答 | 关键数字 |
|---|---|---|
| 准不准 | 能出图，但都不够业务用 | 滑坡 IoU 0.262、光学水体 0.107、SAR 阈值 0.267 |
| 换数据还行吗 | 最薄的一环 | 10 场洪水从 0.229 到 0.003；GSD 差一个量级 |
| 能上平台吗 | 骨架能搬，感知要重训 | 76 件直迁；13 个权重里 7 改、4 训、2 弃 |

## 精度由目标大小决定

| 档位 | 滑坡模型 | 光学水体模型 | SAR 阈值（零模型） |
|---|---:|---:|---:|
| 第 1 档 | 0.005 | 0.004 | 0.045 |
| 第 2 档 | 0.081 | 0.042 | 0.255 |
| 第 3 档 | 0.176 | 0.087 | 0.327 |
| 第 4 档 | 0.340 | 0.198 | 0.547 |
| 第 5 档 | 0.549 | 0.390 | 0.575 |

三个方法、两个数据集、三种架构，同一条单调曲线——这不是某个检查点的毛病。

## 均值会骗人

| 任务 | 均值 | 中位数 | 零检出 |
|---|---:|---:|---:|
| 滑坡（176 张） | 0.262 | 0.090 | 65 张（37%） |
| 光学水体（83 张） | 0.107 | 0.000 | 54 张（65%） |

## 可迁移性

| 级别 | 件数 | 含义 |
|---|---:|---|
| A 直迁 | 76 | 纯算法，改数据根即可 |
| B 改造 | 11 | 有权重，守住三条红线可用 |
| C 重训 | 11 | 输入契约不兼容 |
| D 弃用 | 10 | 业务无交集 |
"""

APPENDIX_D = """# 附录 D · 术语

| 术语 | 含义 |
|---|---|
| **IoU** | 交并比 = 交集 / 并集。分割任务的通用指标，0 表示完全不重合、1 表示完全一致 |
| **F1 / P / R** | F1 = 精确率与召回率的调和平均；P = 检出的里有多少是对的；R = 真值里检出了多少 |
| **掩膜（mask）** | 与影像同尺寸的图，每个像元存一个类别值或 0/255 二值 |
| **GSD** | 地面采样距离，即一个像元对应的地面边长（米）。0.8 m 比 10 m 细 |
| **单期 / 双时相** | 单期 = 只有一张影像；双时相 = 灾前灾后各一张，模型吃两张 |
| **SAR** | 合成孔径雷达。能穿云，汛期是光学失效时的替代；常用 VV/VH 极化 |
| **后向散射** | SAR 的观测量，水面通常很暗（低 dB），因此可用阈值提水体 |
| **分箱** | 把样本按某个量（如目标占比）切成若干区间再统计，用于看趋势 |
| **一致性 / 精度** | 一致性 = 两次预测之间比（无需真值）；精度 = 与人工标注比。两者不可混用 |
| **契约** | 模型对输入的硬性要求：波段数、顺序、归一化常量、窗口尺寸、GSD |
"""

QUICKSTART = """# 快速开始

## 这个仓库是什么

DORA 工具库的**可读版**：108 件 MCP 工具，按功能域重新组织的中文说明，配套一份未经改动的代码副本。

- 代码：`src/dora/tools/`，与上游 1:1，可直接 `import`
- 文档：`docs/`，每域一个 README（速查表）+ 每工具一页（详情）
- 索引：`index/index.html`（可搜索）、`index/tools.json`（机器可读）

## 三类读者，三条路径

| 你想做什么 | 去哪 |
|---|---|
| 快速找一个能用的工具 | 打开 `index/index.html`，搜关键词或按域筛选 |
| 搞清某件工具怎么调 | 进 `docs/<域>/<工具>.md`，看「调用」一节 |
| 判断能不能用在国产数据上 | 看工具页的「适用边界」+ `docs/99-附录/A-接入红线.md` |

## 装起来跑

```bash
pip install -e .                 # 纯算法工具（栅格/矢量/制图/计算）
pip install -e ".[perception]"   # 再加 13 个感知模型所需的 torch 等
```

工具的输出目录由 `--temp_dir` 指定，模型权重放在 `$DORA_DATA/checkpoints/`：

```bash
export DORA_DATA=/path/to/data          # Windows: set DORA_DATA=D:\\data
python -m dora.tools.analysis --temp_dir ./out
```

## 最小可跑示例（无需任何权重）

```python
import json
from dora.tools.analysis import ras_threshold
from dora.tools.calculate import ras_area

json.loads(ras_threshold("dem.tif", 100, op="<", band=1))   # 低于 100 m 的区域
json.loads(ras_area("mask.png", pixel_size_m=10.0))          # 面积（平方米）
```

`scripts/smoke_test.py` 会自动造一张 64×64 的测试栅格并跑通这条链，用来确认环境没问题。

## 阅读约定

- 每件工具页顶部有一行标签：**相关性**（★★★/★★/★/○，与水旱业务的关系）与 **可迁移性**（A/B/C/D，搬到新平台要付多少代价）。两者含义见 `docs/01-工具全景.md`。
- 标注「未实测」的，表示结论来自代码契约推断，没有跑过真实数据。
"""

OVERVIEW_MD = """# 工具全景

## 108 件，两种切法

同一批工具可以用两种视角看。**上游按 MCP 服务切**（部署视角，一个服务一个进程）；
**本仓库按功能域切**（使用视角，找工具时按「我要干什么」找）。

| MCP 服务 | 件数 | 启动命令 | 对应源码 |
|---|---:|---|---|
| Perception | 31 | `python -m dora.tools.perception` | `src/dora/tools/perception.py` |
| Analysis | 41 | `python -m dora.tools.analysis` | `src/dora/tools/analysis.py` |
| Calculate | 15 | `python -m dora.tools.calculate` | `src/dora/tools/calculate.py` |
| Vis | 11 | `python -m dora.tools.vis` | `src/dora/tools/vis.py` |
| POI | 8 | `python -m dora.tools.poi` | `src/dora/tools/poi.py` |
| Model | 2 | `python -m dora.tools.model` | `src/dora/tools/model.py` |

## 相关性：与水旱业务的关系

| 级别 | 件数 | 判据 |
|---|---:|---|
| ★★★ 高度相关 | 36 | 业务链上会直接调用，不接就少一块能力 |
| ★★ 可能相关 | 52 | 与题材无关但流程必需：统计、几何、制图、编排 |
| ★ 弱相关 | 10 | 只在特定子场景出现 |
| ○ 基本无关 | 10 | 与本项目无交集 |

## 可迁移性：搬到新平台要付多少代价

| 级别 | 件数 | 判据 | 迁移动作 |
|---|---:|---|---|
| A 直迁 | 76 | 无训练权重，结果不依赖 GSD / 波段顺序 / 时相 | 改 `DORA_DATA` 即可 |
| B 改造 | 11 | 有权重，但输入域相容；精度够「看」不够「出数」 | 守住三条红线，必要时重标定 |
| C 重训 | 11 | 输入契约不兼容（波段/视角/分辨率/时相） | 重训或重标定 |
| D 弃用 | 10 | 业务无交集 | 不迁 |

两个维度交叉后最值得注意的一点：**★★★ 的 36 件里，必须重训的 4 件恰好是滑坡、水库、洪水、航拍水体**
——也就是淹没范围、水域面积、滑坡这三个业务主指标。骨架能搬，感知要重训。

## 为什么这么切，以及各域件数

上游按「一个进程一个服务」切（部署视角），6 个文件里 `analysis.py` 一个就装了 4296 行、41 件工具，
里面同时住着栅格统计、矢量叠加、路网最短路和 DEM 派生。找工具时按「我要干什么」比按「它跑在哪个进程」更快，
所以文档按 9 个功能域重组；代码目录仍与上游一致，避免两份代码分叉。

| 功能域 | 件数 | 其中 ★★★ | 说明 |
|---|---:|---:|---|
| 10-水体与淹没 | 3 | 3 | 淹没、水域、航拍水体；全部 B/C 档 |
| 20-承灾体 | 14 | 3 | 建筑、道路、桥梁、车辆、储罐、港口、重建 |
| 30-地形与地表变化 | 5 | 5 | 两个滑坡模型 + 植被 + 坡度/山影 |
| 40-栅格分析 | 15 | 10 | 面积、统计、阈值、裁剪、拼接、重采样、矢量化 |
| 50-矢量与空间关系 | 24 | 6 | 叠加、几何、路网 |
| 60-计算与决策 | 15 | 2 | 标量运算、决策规则、编排 |
| 70-制图与报告 | 13 | 7 | 专题图、拼图、报告页、摘要 |
| 80-POI-点位 | 8 | 0 | 设施与人口暴露 |
| 90-其他感知 | 11 | 0 | 与本项目无关，保留为台账完整 |

跨域工具只归主域（如 `ras.diff` 主域在栅格分析，地形页以「相关但不在本域」交叉引用），
不做重复页面，避免同一件工具两处说法不一致。
"""
