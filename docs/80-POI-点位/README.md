# 80-POI-点位

8 件，点位数据与灾害的交叉。输入是 GeoJSON 点（学校、医院、水厂、安置点），
输出是「哪些点落进了受损建筑或淹没区、涉及多少人口、按什么优先级处置」。依赖 geopandas，无权重。

这一域的价值在于把「空间范围」翻译成「人和设施」——指挥决策关心的是后者。

## 工具速查（8 件）

| 工具 | 相关性 | 可迁移性 | 用途 |
|---|---|---|---|
| [`poi.damage_population_exposure`](poi.damage_population_exposure.md) | ★★ | A | 受影响人口优先序 |
| [`poi.filter_by_attribute`](poi.filter_by_attribute.md) | ★★ | A | 只看医院/学校/水厂 |
| [`poi.filter_by_damage`](poi.filter_by_damage.md) | ★★ | A | 学校/医院受淹排查 |
| [`poi.group_by`](poi.group_by.md) | ★★ | A | 按行政区/地类汇总 |
| [`poi.to_vector`](poi.to_vector.md) | ★★ | A | POI 数据入库 |
| [`poi.world_to_pixel`](poi.world_to_pixel.md) | ★★ | A | 把业务点位对齐到卫星影像 |
| [`poi.filter_by_intact`](poi.filter_by_intact.md) | ★ | A | 可用资源点 |
| [`poi.search_by_name`](poi.search_by_name.md) | ★ | A | 按地名定位 |

## 相关但不在本域

- `poi.world_to_pixel`：把业务点位对齐到影像
- `poi.filter_by_damage`：筛出位于受损建筑内的点
- `logi.priority_score`（60）：按人口/损失排序

## 列的含义

- **相关性**：★★★ 业务直接调用 / ★★ 流程必需 / ★ 特定子场景 / ○ 无交集
- **可迁移性**：A 零改造直迁 / B 加规范可用 / C 必须重训 / D 不建议迁
- 判定依据见 [`01-工具全景`](../01-工具全景.md) 与 [`99-附录/A-接入红线`](../99-附录/A-接入红线.md)
