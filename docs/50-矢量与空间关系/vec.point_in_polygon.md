# `vec.point_in_polygon`

> 站点/村庄是否位于淹没区或风险区

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:4097`（35 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> For each input point, test whether it lies inside any polygon of a polygon layer. Returns the matching polygon id(s) if any. Useful for filtering POIs to those located within damaged zones.

## 这个工具做什么

判断一个点是不是落在某个范围里。村子在不在淹没区、站点在不在风险区，一问就知道。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `points_path` | str | 是 | — | 点要素文件（GeoJSON） |
| `polygons_path` | str | 是 | — | Path to polygon GeoJSON |
| `polygon_id_field` | str? | 否 | `None` | Attribute field used as polygon identifier |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `matches` | list[dict | List of {point_index, polygon_ids} for inside points |
| `inside_count` | int | Number of points located inside at least one polygon |

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_point_in_polygon
import json

res = json.loads(vec_point_in_polygon(points_path="input.tif", polygons_path="input.tif"))
print(res)
```

```json
{
  "name": "vec.point_in_polygon",
  "arguments": {
    "points_path": "input.tif",
    "polygons_path": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 站点/村庄是否位于淹没区或风险区
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
