# `seg.water_aerial`

> 应急航拍精细淹没边界

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:952`（2 行） |
| 相关性 | ★★★ |
| 可迁移性 | C（0.03 m 航拍） |
| 依赖 | 模型 DPT-aerial |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Segment water areas from post-disaster optical airborne image. Spatial resolution: 0.03m.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `post_image_path` | str | 是 | — | 灾后影像路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to water mask (255 = water) |
| `classes` | dict | {11: "water"} |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 DPT-aerial
- 硬件：需模型权重；CPU 可跑但慢（秒级/MP），建议 GPU（未实测）
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_water_aerial
import json

res = json.loads(seg_water_aerial(post_image_path="post.tif"))
print(res)
```

```json
{
  "name": "seg.water_aerial",
  "arguments": {
    "post_image_path": "post.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 应急航拍精细淹没边界
- **可迁移性**：C（0.03 m 航拍）
- 0.03 m 航拍专用，星载影像上目标尺度不符。有航次时它是最精细的边界来源。

## 相关工具

- [`vis.overlay_mask`](../70-制图与报告/vis.overlay_mask.md)
- [`ras.area`](../40-栅格分析/ras.area.md)

---

[← 返回 10-水体与淹没](README.md)　·　[工具总表](../../index/INDEX.md)
