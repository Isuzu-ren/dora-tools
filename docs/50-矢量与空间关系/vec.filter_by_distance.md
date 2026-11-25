# `vec.filter_by_distance`

> 以水库/险工段为中心的影响范围筛选

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:3233`（6 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Filter vector features by distance from a center point (WGS84).

## 这个工具做什么

只保留离某个中心点一定距离内的要素，比如水库周边 2 公里内的村庄。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_path` | str | 是 | — | 矢量路径（GeoJSON） |
| `center_lat` | float | 是 | — | Center point latitude (WGS84) |
| `center_lon` | float | 是 | — | Center point longitude (WGS84) |
| `max_distance_m` | float | 是 | — | 最大搜索距离（米） |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `vector_path` | str | Path to filtered vector |
| `total_input` | int | Number of input features |
| `total_filtered` | int | Number of features within distance |
| `nearest_distance_m` | float | Distance to nearest feature |
| `farthest_distance_m` | float | Distance to farthest feature |

**落盘产物**：`vector_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_filter_by_distance_tool
import json

res = json.loads(vec_filter_by_distance_tool(vector_path="admin.geojson", center_lat="0.0", center_lon="0.0", max_distance_m="0.0"))
print(res)
```

```json
{
  "name": "vec.filter_by_distance",
  "arguments": {
    "vector_path": "admin.geojson",
    "center_lat": "0.0",
    "center_lon": "0.0",
    "max_distance_m": "0.0"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：images/heatisland/09LD1638/osm/buildings.geojson（79 个建筑面，已转 EPSG:6677）

```json
{
  "vector_path": "<work>/fixtures/buildings.geojson",
  "center_lat": 35.69,
  "center_lon": 139.7,
  "max_distance_m": 800.0
}
```

### 示例输出

```json
{
  "tool": "vec.filter_by_distance",
  "vector_path": "<temp_dir>/filtered_by_distance_d58d6d.geojson",
  "center_lat": 35.69,
  "center_lon": 139.7,
  "max_distance_m": 800.0,
  "total_input": 79,
  "total_filtered": 0,
  "nearest_distance_m": null,
  "farthest_distance_m": null
}
```

耗时 0.02 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— 以水库/险工段为中心的影响范围筛选
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
