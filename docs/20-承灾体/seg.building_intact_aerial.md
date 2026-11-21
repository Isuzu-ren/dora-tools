# `seg.building_intact_aerial`

> 同上

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:794`（3 行） |
| 相关性 | ★ |
| 可迁移性 | C（0.03 m 航拍） |
| 依赖 | 模型 DPT-aerial |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Segment building-no-damage areas from post-disaster optical airborne image. Spatial resolution: 0.03m.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `post_image_path` | str | 是 | — | 灾后影像路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to building_no_damage mask (255 = building_no_damage) |
| `classes` | dict | {1: "building_no_damage"} |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 DPT-aerial
- 硬件：需模型权重；CPU 可跑但慢（秒级/MP），建议 GPU（未实测）
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_building_intact_aerial
import json

res = json.loads(seg_building_intact_aerial(post_image_path="post.tif"))
print(res)
```

```json
{
  "name": "seg.building_intact_aerial",
  "arguments": {
    "post_image_path": "post.tif"
  }
}
```

## 适用边界

- **相关性**：★ —— 同上
- **可迁移性**：C（0.03 m 航拍）
- 输入契约与新数据不兼容，直接推会静默失效；本件未做专项实测，判断依据是代码契约（波段 / 视角 / 分辨率）。

---

[← 返回 20-承灾体](README.md)　·　[工具总表](../../index/INDEX.md)
