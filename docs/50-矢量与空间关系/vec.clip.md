# `vec.clip`

> 裁到流域/行政区边界

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:3397`（48 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Clip input vectors by ROI vectors.

## 这个工具做什么

用一块多边形去裁矢量数据，只保留范围内的部分。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_path` | str | 是 | — | 矢量路径（GeoJSON） |
| `roi_vector_path` | str | 是 | — | Path to ROI vector GeoJSON (Polygon/MultiPolygon recommended) |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `clip_path` | str | Path to clipped GeoJSON |
| `input_count` | int | number of input features |
| `output_count` | int | number of output features |

**落盘产物**：`clip_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_clip
import json

res = json.loads(vec_clip(vector_path="admin.geojson", roi_vector_path="admin.geojson"))
print(res)
```

```json
{
  "name": "vec.clip",
  "arguments": {
    "vector_path": "admin.geojson",
    "roi_vector_path": "admin.geojson"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：images/heatisland/09LD1638/osm/buildings.geojson（79 个建筑面，已转 EPSG:6677）；覆盖 buildings 西半幅的矩形，用作裁剪范围

```json
{
  "vector_path": "<work>/fixtures/buildings.geojson",
  "roi_vector_path": "<work>/fixtures/roi.geojson"
}
```

[![示例输入](../../examples/50-矢量与空间关系/vec.clip/in.webp)](../../examples/50-矢量与空间关系/vec.clip/in.webp)

### 示例输出

```json
{
  "tool": "vec.clip",
  "clip_path": "<temp_dir>/buildings_CLIP_roi.geojson_be9b87_c1a97a.geojson",
  "input_count": 79,
  "output_count": 42,
  "input_vector": "<work>/fixtures/buildings.geojson",
  "roi_vector": "<work>/fixtures/roi.geojson"
}
```

[![示例输出](../../examples/50-矢量与空间关系/vec.clip/out.webp)](../../examples/50-矢量与空间关系/vec.clip/out.webp)

*示例输出*（点击图片看原图）

耗时 0.04 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— 裁到流域/行政区边界
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
