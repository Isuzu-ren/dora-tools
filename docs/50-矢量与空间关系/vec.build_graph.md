# `vec.build_graph`

> 通行能力建模

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:2538`（76 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | networkx |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Build a road graph from centerline GeoJSON. Nodes are endpoints of each line, edges carry pixel coordinates and length.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `centerline_path` | str | 是 | — | Path to centerline GeoJSON (LineString geometries, pixel space) |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `graph_path` | str | Path to saved graph pickle (networkx graphml) |

**落盘产物**：`graph_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：networkx
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import build_road_graph
import json

res = json.loads(build_road_graph(centerline_path="input.tif"))
print(res)
```

```json
{
  "name": "vec.build_graph",
  "arguments": {
    "centerline_path": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★ —— 通行能力建模
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

## 已知坑与建议

- **建议**：路网分析三步走：`road_centerline_extraction` → `build_graph` → `graph_shortest_path`。

## 相关工具

- [`vec.road_centerline_extraction`](vec.road_centerline_extraction.md)
- [`vec.graph_shortest_path`](vec.graph_shortest_path.md)

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
