# `seg.harbor`

> 内河/沿海码头受影响范围

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:606`（2 行） |
| 相关性 | ★ |
| 可迁移性 | B（0.5–1 m） |
| 依赖 | 模型 DPT-isaid |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Segment harbors from post-disaster optical satellite image. Spatial resolution: 0.5m-1.0m.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `post_image_path` | str | 是 | — | 灾后影像路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to binary harbor mask (255 = harbor) |
| `classes` | dict | {15: harbor} |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 DPT-isaid
- 硬件：需模型权重；CPU 可跑但慢（秒级/MP），建议 GPU（未实测）
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_harbor
import json

res = json.loads(seg_harbor(post_image_path="post.tif"))
print(res)
```

```json
{
  "name": "seg.harbor",
  "arguments": {
    "post_image_path": "post.tif"
  }
}
```

## 适用边界

- **相关性**：★ —— 内河/沿海码头受影响范围
- **可迁移性**：B（0.5–1 m）
- 有权重、域内可用，但必须守住三条红线；本件未做专项实测，接入前请目视复核 10–20 景。
- 本域统一的输入口径（分辨率 / 时相 / 是否实测）见 [README 的「实测口径」表](README.md#实测口径)

---

[← 返回 20-承灾体](README.md)　·　[工具总表](../../index/INDEX.md)
