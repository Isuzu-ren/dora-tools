# 70-制图与报告

13 件 = 11 件制图 + 2 件汇总（证据抽取、LLM 摘要）。

预警平台的最后一公里不是数字，是一张能发出去的图：`vis.damage_map` 出专题图，
`vis.temporal_panel` 出涨水—峰值—退水序列，`vis.report_page` 出一页式值班简报。
除 `model.summarize` 需要 LLM 接口外，其余全部无权重。

## 工具速查（13 件）

| 工具 | 相关性 | 可迁移性 | 用途 |
|---|---|---|---|
| [`model.summarize`](model.summarize.md) | ★★★ | B（换 LLM 端点） | 值班简报文字；需 API Key，数据出境需评估 |
| [`vis.add_map_elements`](vis.add_map_elements.md) | ★★★ | A | 成品图规范化 |
| [`vis.before_after_panel`](vis.before_after_panel.md) | ★★★ | A | 汛前汛后对比 |
| [`vis.damage_map`](vis.damage_map.md) | ★★★ | A | 预警产品出图 |
| [`vis.overlay_mask`](vis.overlay_mask.md) | ★★★ | A | 淹没范围图 |
| [`vis.report_page`](vis.report_page.md) | ★★★ | A | 值班简报 |
| [`vis.temporal_panel`](vis.temporal_panel.md) | ★★★ | A | 水情/旱情演变序列（涨水—峰值—退水） |
| [`report.extract_evidence`](report.extract_evidence.md) | ★★ | A | 多步结果的自动汇总，不调模型 |
| [`vis.bar_chart`](vis.bar_chart.md) | ★★ | A | 分区统计展示 |
| [`vis.heatmap`](vis.heatmap.md) | ★★ | A | 隐患点、报汛站、受灾点密度 |
| [`vis.line_chart`](vis.line_chart.md) | ★★ | A | 水位/面积过程线 |
| [`vis.pie_chart`](vis.pie_chart.md) | ★★ | A | 构成占比 |
| [`vis.route_map`](vis.route_map.md) | ★★ | A | 抢险路线图 |

## 相关但不在本域

- `ras.vectorize`（40）：先矢量化再出专题图，边界更干净
- `tool.chart_data`（60）：图表的输入格式
- `report.extract_evidence`：出报告前的证据汇总

## 列的含义

- **相关性**：★★★ 业务直接调用 / ★★ 流程必需 / ★ 特定子场景 / ○ 无交集
- **可迁移性**：A 零改造直迁 / B 加规范可用 / C 必须重训 / D 不建议迁
- 判定依据见 [`01-工具全景`](../01-工具全景.md) 与 [`99-附录/A-接入红线`](../99-附录/A-接入红线.md)
