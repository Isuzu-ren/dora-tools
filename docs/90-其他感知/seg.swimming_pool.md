# `seg.swimming_pool`

> **与本项目无关**：本件不在水旱预警链路上，保留仅为台账完整（108 件与上游一致）。

> 无关

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:561`（2 行） |
| 相关性 | ○ |
| 可迁移性 | D（业务无关） |
| 依赖 | 模型 DPT-isaid |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Segment swimming pools from post-disaster optical satellite image. Spatial resolution: 0.5m-1.0m.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `post_image_path` | str | 是 | — | 灾后影像路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to binary pool mask (255 = swimming_pool) |
| `classes` | dict | {11: swimming_pool} |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 DPT-isaid
- 硬件：需模型权重；CPU 可跑但慢（秒级/MP），建议 GPU（未实测）
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_swimming_pool
import json

res = json.loads(seg_swimming_pool(post_image_path="post.tif"))
print(res)
```

```json
{
  "name": "seg.swimming_pool",
  "arguments": {
    "post_image_path": "post.tif"
  }
}
```

## 适用边界

- **相关性**：○ —— 无关
- **可迁移性**：D（业务无关）
- 与本项目无交集，仅为台账完整而保留。

---

[← 返回 90-其他感知](README.md)　·　[工具总表](../../index/INDEX.md)
