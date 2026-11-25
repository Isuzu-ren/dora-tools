# `seg.pool_aerial`

> **与本项目无关**：本件不在水旱预警链路上，保留仅为台账完整（108 件与上游一致）。

> 无关

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:842`（2 行） |
| 相关性 | ○ |
| 可迁移性 | D（业务无关） |
| 依赖 | 模型 DPT-aerial |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Segment pool areas from post-disaster optical airborne image. Spatial resolution: 0.03m.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `post_image_path` | str | 是 | — | 灾后影像路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to pool mask (255 = pool) |
| `classes` | dict | {4: "pool"} |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 DPT-aerial
- 硬件：需模型权重；CPU 可跑但慢（秒级/MP），建议 GPU（未实测）
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_pool_aerial
import json

res = json.loads(seg_pool_aerial(post_image_path="post.tif"))
print(res)
```

```json
{
  "name": "seg.pool_aerial",
  "arguments": {
    "post_image_path": "post.tif"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：mayfield region_01 无人机影像 0.03 m（裁 1024²）

```json
{
  "post_image_path": "<work>/fixtures/aerial.tif"
}
```

[![示例输入](../../examples/90-其他感知/seg.pool_aerial/in.webp)](../../examples/90-其他感知/seg.pool_aerial/in.webp)

### 示例输出

```json
{
  "mask_path": "<temp_dir>/seg_pool_aerial_mask_b4cf39.png",
  "classes": {
    "4": "pool"
  },
  "mask_value": 255,
  "_meta": {
    "forward_ms": 18238.63
  },
  "tool": "seg.pool_aerial"
}
```

[![示例输出](../../examples/90-其他感知/seg.pool_aerial/out.webp)](../../examples/90-其他感知/seg.pool_aerial/out.webp)

*示例输出*（点击图片看原图）

耗时 23.98 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：○ —— 无关
- **可迁移性**：D（业务无关）
- 与本项目无交集，仅为台账完整而保留。

---

[← 返回 90-其他感知](README.md)　·　[工具总表](../../index/INDEX.md)
