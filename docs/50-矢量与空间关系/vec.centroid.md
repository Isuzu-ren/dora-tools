# `vec.centroid`

> 灾情中心点

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:2280`（5 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Calculate the centroid of a polygon or point feature in a vector file. Useful for finding the center point of the largest damaged area (explosion center).

## 这个工具做什么

算每个图斑的中心点，用来标注「灾情中心在哪」。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_path` | str | 是 | — | 矢量路径（GeoJSON） |
| `feature_idx` | int | 否 | `0` | Index of feature to get centroid for (default: 0, the first feature; use -1 for the largest) |
| `raster_path` | str | 否 | `None` | 栅格路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `feature_idx` | int | The feature index used |
| `geometry_type` | str | Type of the original geometry |

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_centroid_tool
import json

res = json.loads(vec_centroid_tool(vector_path="admin.geojson"))
print(res)
```

```json
{
  "name": "vec.centroid",
  "arguments": {
    "vector_path": "admin.geojson"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：images/heatisland/09LD1638/osm/buildings.geojson（79 个建筑面，已转 EPSG:6677）

```json
{
  "vector_path": "<work>/fixtures/buildings.geojson"
}
```

### 示例输出

```json
{
  "tool": "vec.centroid",
  "feature_idx": 0,
  "geometry_type": "Polygon",
  "latitude": 35.69177906203053,
  "longitude": 139.69547570982024
}
```

耗时 0.04 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— 灾情中心点
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
