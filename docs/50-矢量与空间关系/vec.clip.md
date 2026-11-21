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

## 适用边界

- **相关性**：★★ —— 裁到流域/行政区边界
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
