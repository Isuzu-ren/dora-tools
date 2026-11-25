# `vec.max_polygon`

> 找主淹没区/最大灾区

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:2156`（38 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Find the largest polygon(s) from existing vector data based on area.

## 这个工具做什么

从一堆图斑里挑出最大的那几块，用来定位主灾区。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_path` | str | 是 | — | 矢量路径（GeoJSON） |
| `pixel_size_m` | float | 否 | `None` | 像元边长（米）。掩膜无地理参考时必须显式给出 |
| `topk` | int | 否 | `1` | 取前 k 个 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `max_area_m2` | float | Area of the largest polygon in square meters |
| `max_pixel_count` | int | Pixel count of the largest polygon (if available) |
| `topk_polygons` | list | Top-k polygons by area |
| `total_polygons` | int | Total polygons found |
| `vector_path` | str | Echo of input |

**落盘产物**：`vector_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_max_polygon
import json

res = json.loads(vec_max_polygon(vector_path="admin.geojson"))
print(res)
```

```json
{
  "name": "vec.max_polygon",
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
  "tool": "vec.max_polygon",
  "max_area_m2": 4863.726964112406,
  "max_pixel_count": null,
  "topk_polygons": [
    {
      "pixel_count": null,
      "area_m2": 4863.726964112406
    }
  ],
  "total_polygons": 79,
  "vector_path": "<work>/fixtures/buildings.geojson"
}
```

耗时 0.02 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— 找主淹没区/最大灾区
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
