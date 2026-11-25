# `seg.ship`

> **与本项目无关**：本件不在水旱预警链路上，保留仅为台账完整（108 件与上游一致）。

> 内河航运场景可微调后使用

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:636`（2 行） |
| 相关性 | ○ |
| 可迁移性 | D（业务无关） |
| 依赖 | 模型 DPT-isaid |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Segment ships from post-disaster optical satellite image. Spatial resolution: 0.5m-1.0m.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `post_image_path` | str | 是 | — | 灾后影像路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to binary ship mask (255 = ship) |
| `classes` | dict | {1: ship} |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 DPT-isaid
- 硬件：需模型权重；CPU 可跑但慢（秒级/MP），建议 GPU（未实测）
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_ship
import json

res = json.loads(seg_ship(post_image_path="post.tif"))
print(res)
```

```json
{
  "name": "seg.ship",
  "arguments": {
    "post_image_path": "post.tif"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：xbd guatemala_volcano_00000004 灾后影像（0.8 m，1024²，RGB）

```json
{
  "post_image_path": "<DORA_DATA>/images/xbd_agent_benchv1/post/guatemala_volcano_00000004_post.png"
}
```

[![示例输入](../../examples/90-其他感知/seg.ship/in.webp)](../../examples/90-其他感知/seg.ship/in.webp)

### 示例输出

```json
{
  "mask_path": "<temp_dir>/seg_ship_mask_bc4052.png",
  "mask_value": 255,
  "_meta": {
    "forward_ms": 17908.64
  },
  "tool": "seg.ship"
}
```

[![示例输出](../../examples/90-其他感知/seg.ship/out.webp)](../../examples/90-其他感知/seg.ship/out.webp)

*示例输出*（点击图片看原图）

耗时 17.97 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：○ —— 内河航运场景可微调后使用
- **可迁移性**：D（业务无关）
- 与本项目无交集，仅为台账完整而保留。

---

[← 返回 90-其他感知](README.md)　·　[工具总表](../../index/INDEX.md)
