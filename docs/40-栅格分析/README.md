# 40-栅格分析

16 件，全部无权重，是全库复用价值最高、迁移成本最低的一组：面积、统计、阈值、裁剪、
拼接、重采样、重投影、矢量化都在这里。

上线时「从掩膜到结论」这条尾巴——面积换算、分区统计、投影统一、出图前的矢量化——主要由本域
加矢量域承担。注意 `ras.diff` 与 `ras.focal_stats` 虽常用于地形，但对任意栅格通用，因此归在本域。

## 工具速查（16 件）

| 工具 | 相关性 | 可迁移性 | 用途 |
|---|---|---|---|
| [`ras.area`](ras.area.md) | ★★★ | A | 淹没面积、受旱面积、水域面积 |
| [`ras.concat`](ras.concat.md) | ★★★ | A | 构造 14 波段输入（多光谱 + DEM + 坡度）的必经步骤 |
| [`ras.diff`](ras.diff.md) | ★★★ | A | 多期差值、DSM−DEM 求相对高度 |
| [`ras.focal_stats`](ras.focal_stats.md) | ★★★ | A | 热点检测、平滑、DEM 局部粗糙度 |
| [`ras.grid_windows`](ras.grid_windows.md) | ★★★ | A | 面雨量/旱情分区统计的基础 |
| [`ras.index`](ras.index.md) | ★★★ | A | 任意两波段的归一化差值指数（NDVI/NDWI/NDMI/NBR），干旱监测的基础算子 |
| [`ras.reproject`](ras.reproject.md) | ★★★ | A | 多源数据统一坐标系（国产影像常为 CGCS2000） |
| [`ras.resample`](ras.resample.md) | ★★★ | A | 统一 GSD：模型对分辨率敏感，这一步不能省 |
| [`ras.stats`](ras.stats.md) | ★★★ | A | 水位/温度/降水量的区域统计 |
| [`ras.threshold`](ras.threshold.md) | ★★★ | A | 最通用的一招：LST/NDVI/水深/降水栅格都能阈值化 |
| [`ras.vectorize`](ras.vectorize.md) | ★★★ | A | 淹没范围出图、与行政区叠加的前提 |
| [`mask.compose_multiclass`](mask.compose_multiclass.md) | ★★ | A | 把「常水体/新增水体/退水」合成一张图 |
| [`ras.clip`](ras.clip.md) | ★★ | A | 按流域/行政区裁切 |
| [`ras.count_pixels`](ras.count_pixels.md) | ★★ | A | 面积前的中间量 |
| [`ras.sample_point`](ras.sample_point.md) | ★★ | A | 站点/断面取值 |
| [`ras.sample_points`](ras.sample_points.md) | ★★ | A | 水文站点批量采样 |

## 相关但不在本域

- `vec.raster_stats`（50-矢量与空间关系）：按行政区/流域汇总
- `tool.loop`（60-计算与决策）：按网格批量算
- `ras.vectorize` → `vis.damage_map`（70）：出图链路

## 列的含义

- **相关性**：★★★ 业务直接调用 / ★★ 流程必需 / ★ 特定子场景 / ○ 无交集
- **可迁移性**：A 零改造直迁 / B 加规范可用 / C 必须重训 / D 不建议迁
- 判定依据见 [`01-工具全景`](../01-工具全景.md) 与 [`99-附录/A-接入红线`](../99-附录/A-接入红线.md)
