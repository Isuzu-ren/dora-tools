# `seg.vehicle_free_aerial`

> **与本项目无关**：本件不在水旱预警链路上，保留仅为台账完整（108 件与上游一致）。

> 对照类别

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:920`（3 行） |
| 相关性 | ○ |
| 可迁移性 | D（业务无关） |
| 依赖 | 模型 DPT-aerial |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Segment non-trapped vehicle areas from post-disaster optical airborne image. Spatial resolution: 0.03m.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `post_image_path` | str | 是 | — | 灾后影像路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to vehicle_not_trapped mask (255 = vehicle_not_trapped) |
| `classes` | dict | {9: "vehicle_not_trapped"} |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 DPT-aerial
- 硬件：需模型权重；CPU 可跑但慢（秒级/MP），建议 GPU（未实测）
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_vehicle_free_aerial
import json

res = json.loads(seg_vehicle_free_aerial(post_image_path="post.tif"))
print(res)
```

```json
{
  "name": "seg.vehicle_free_aerial",
  "arguments": {
    "post_image_path": "post.tif"
  }
}
```

## 适用边界

- **相关性**：○ —— 对照类别
- **可迁移性**：D（业务无关）
- 与本项目无交集，仅为台账完整而保留。

---

[← 返回 90-其他感知](README.md)　·　[工具总表](../../index/INDEX.md)
