# `vec.graph_shortest_path`

> 抢险/撤离路径规划

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:2720`（62 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | networkx |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Find shortest path on an intact-road graph.

## 这个工具做什么

在路网上找最短或最快的一条路。抢险车怎么开、群众往哪撤，靠它规划。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `graph_path` | str | 是 | — | 路网图文件路径 |
| `start` | list[int] | 是 | — | [row, col] start point (pixel coordinates) |
| `end` | list[int] | 是 | — | [row, col] end point (pixel coordinates) |
| `pixel_size_m` | float | 否 | `1.0` | 像元边长（米）。掩膜无地理参考时必须显式给出 |
| `snap_buffer_px` | int | 否 | `SNAP_BUFFER_PX` | — |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `distance_px` | float|null | Shortest path length in pixels (null if no path) |
| `distance_m` | float|null | Shortest path length in meters (null if no path) |
| `path_pixels` | list | List of [row, col] along path |
| `path_geojson` | str|null | Path to saved path GeoJSON (null if no path) |

## 依赖与运行

- 依赖：networkx
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import graph_shortest_path
import json

res = json.loads(graph_shortest_path(graph_path="input.tif", start="input.tif", end="input.tif"))
print(res)
```

```json
{
  "name": "vec.graph_shortest_path",
  "arguments": {
    "graph_path": "input.tif",
    "start": "input.tif",
    "end": "input.tif"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：vec.build_graph 生成的路网图（Tokyo OSM 道路）

```json
{
  "graph_path": "<work>/fixtures/graph.graphml",
  "start": [
    -34127,
    -12767
  ],
  "end": [
    -33913,
    -12687
  ],
  "pixel_size_m": 0.2
}
```

### 示例输出

```json
{
  "tool": "vec.graph_shortest_path",
  "distance_px": 9.0,
  "distance_m": 1.8,
  "path_pixels": [
    [
      -34127,
      -12767
    ],
    [
      -34118,
      -12768
    ],
    [
      -34087,
      -12774
    ],
    "…（共 10 条，此处省略）"
  ],
  "path_geojson": "<temp_dir>/road_path_781d76.geojson",
  "snapped_start": [
    -34127,
    -12767
  ],
  "snapped_end": [
    -33913,
    -12687
  ],
  "snapped_on_damaged": false,
  "snap_failed": false
}
```

> 起点终点是像素坐标；图与影像必须同坐标系。

耗时 0.02 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— 抢险/撤离路径规划
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
