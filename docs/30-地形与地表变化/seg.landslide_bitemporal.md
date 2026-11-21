# `seg.landslide_bitemporal`

> 无 DEM 时的替代路径

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:418`（15 行） |
| 相关性 | ★★★ |
| 可迁移性 | B（未实测） |
| 依赖 | 模型 SwinUperNet 6ch |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Segment landslide from pre/post disaster optical satellite images (bi-temporal change detection). Spatial resolution: 0.59m.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `pre_image_path` | str | 是 | — | 灾前影像路径 |
| `post_image_path` | str | 是 | — | 灾后影像路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to the saved landslide mask image |
| `classes` | dict | Mapping of class values |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 SwinUperNet 6ch
- 硬件：需模型权重；CPU 可跑但慢（秒级/MP），建议 GPU（未实测）
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_landslide_bitemporal
import json

res = json.loads(seg_landslide_bitemporal(pre_image_path="pre.tif", post_image_path="post.tif"))
print(res)
```

```json
{
  "name": "seg.landslide_bitemporal",
  "arguments": {
    "pre_image_path": "pre.tif",
    "post_image_path": "post.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 无 DEM 时的替代路径
- **可迁移性**：B（未实测）
- 0.59 m、双时相、3 波段，**不需要 DEM**——是没有 DEM 数据时的替代路径。精度未实测。

## 相关工具

- [`seg.landslide_ms`](seg.landslide_ms.md)
- [`ras.diff`](../40-栅格分析/ras.diff.md)

---

[← 返回 30-地形与地表变化](README.md)　·　[工具总表](../../index/INDEX.md)
