# `vec.repair_min_edges`

> 断路情况下最小抢通方案

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:4164`（127 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | networkx |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Given a road graph with some edges marked as damaged/blocked, find the minimum set of edges that must be repaired so that a shortest path between source and target nodes becomes possible. The solution minimises the number of repairs first and breaks ties by total path length. The graph may be provided as a NetworkX .graphml file (output of vec.build_graph) or as a JSON file with {"nodes": [...], "edges": [...]}. If source/target are not given or do not exist in the graph, the function automatically selects two nodes from the largest connected component: a node near the centroid of the componen

## 这个工具做什么

算「最少修哪几段路，就能让所有孤立的点重新连上」，用于断路后的抢通排序。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `graph_path` | str | 是 | — | 路网图文件路径 |
| `source` | str | int? | 否 | `None` | Source node id (e.g., a rescue base). If omitted |
| `target` | str | int? | 否 | `None` | Target node id (e.g., a hospital). Same rule. |
| `blocked_attr` | str | 否 | `'damaged'` | Edge attribute marking a damaged/blocked edge. |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `repair_edges` | list | Edge endpoints that must be repaired, e.g. [[u, v], ...] |
| `repair_count` | int | Minimum number of repairs needed on the optimal path |
| `path_length_m` | float | Total length of the post-repair path (metres) |
| `source` | int | Source node id actually used |
| `target` | int | Target node id actually used |
| `auto_selected` | bool | Whether source/target were auto-selected |

## 依赖与运行

- 依赖：networkx
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_repair_min_edges
import json

res = json.loads(vec_repair_min_edges(graph_path="input.tif"))
print(res)
```

```json
{
  "name": "vec.repair_min_edges",
  "arguments": {
    "graph_path": "input.tif"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：vec.build_graph 生成的路网图（JSON）

```json
{
  "graph_path": "<work>/fixtures/graph.graphml"
}
```

### 示例输出

```json
{
  "tool": "vec.repair_min_edges",
  "repair_edges": [],
  "repair_count": 0,
  "path_length_m": 20.0,
  "path_node_count": 11,
  "source": 17,
  "target": 219,
  "auto_selected": true,
  "blocked_attr": "damaged",
  "graph_nodes": 300,
  "graph_edges": 206
}
```

耗时 0.03 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— 断路情况下最小抢通方案
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

## 已知坑与建议

- **建议**：「最少抢通哪几段」——溃堤、断路场景下比最短路更贴近指挥决策。

## 相关工具

- [`vec.build_graph`](vec.build_graph.md)

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
