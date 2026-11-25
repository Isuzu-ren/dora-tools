# `vec.nearest`

> 受灾点最近的安置点/物资库

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:3260`（122 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> For each feature in vector A, find the nearest feature(s) in vector B using Euclidean (straight-line) distance in pixel space.

## 这个工具做什么

给一个点，找出离它最近的另一类设施——受灾点最近的安置点、最近的物资库。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_a_path` | str | 是 | — | 矢量层 A（GeoJSON） |
| `vector_b_path` | str | 是 | — | 矢量层 B（GeoJSON） |
| `pixel_size_m` | float | 否 | `None` | 像元边长（米）。掩膜无地理参考时必须显式给出 |
| `topk` | int | 否 | `1` | 取前 k 个 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `table_path` | str | CSV with nearest pairs and distances |
| `links_geojson` | str|None | GeoJSON of A–B nearest connectors |

**落盘产物**：`table_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_polygon_nearest
import json

res = json.loads(vec_polygon_nearest(vector_a_path="admin.geojson", vector_b_path="admin.geojson"))
print(res)
```

```json
{
  "name": "vec.nearest",
  "arguments": {
    "vector_a_path": "admin.geojson",
    "vector_b_path": "admin.geojson"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：images/heatisland/09LD1638/osm/buildings.geojson（79 个建筑面，已转 EPSG:6677）；同目录 points.geojson（OSM 点要素，已转 EPSG:6677）

```json
{
  "vector_a_path": "<work>/fixtures/buildings.geojson",
  "vector_b_path": "<work>/fixtures/points.geojson"
}
```

### 示例输出

```json
{
  "distance_px": null,
  "distance_m": 0.0,
  "nearest_a_id": 1,
  "nearest_b_id": 1,
  "tool": "vec.nearest",
  "mode": "euclidean",
  "topk": 1,
  "pair_count": 79,
  "pixel_size_m": null,
  "table_path": "<temp_dir>/vec_nearest_table_daf3ff.csv",
  "links_geojson": "<temp_dir>/vec_nearest_links_5b313b.geojson",
  "vector_a_path": "<work>/fixtures/buildings.geojson",
  "vector_b_path": "<work>/fixtures/points.geojson"
}
```

耗时 0.57 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— 受灾点最近的安置点/物资库
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
