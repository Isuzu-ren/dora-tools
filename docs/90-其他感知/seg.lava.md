# `seg.lava`

> **与本项目无关**：本件不在水旱预警链路上，保留仅为台账完整（108 件与上游一致）。

> 火山专用

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:322`（13 行） |
| 相关性 | ○ |
| 可迁移性 | D（业务无关） |
| 依赖 | 模型 BitemporalDPT 6ch |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Segment volcano lava from pre/post disaster optical satellite images. Spatial resolution: 0.8m. The input pre and post image requires 3-bands.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `pre_image_path` | str | 是 | — | 灾前影像路径 |
| `post_image_path` | str | 是 | — | 灾后影像路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to the saved lava mask image |
| `classes` | dict | Mapping of class values |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 BitemporalDPT 6ch
- 硬件：需模型权重；CPU 可跑但慢（秒级/MP），建议 GPU（未实测）
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_lava
import json

res = json.loads(seg_lava(pre_image_path="pre.tif", post_image_path="post.tif"))
print(res)
```

```json
{
  "name": "seg.lava",
  "arguments": {
    "pre_image_path": "pre.tif",
    "post_image_path": "post.tif"
  }
}
```

## 适用边界

- **相关性**：○ —— 火山专用
- **可迁移性**：D（业务无关）
- 与本项目无交集，仅为台账完整而保留。

---

[← 返回 90-其他感知](README.md)　·　[工具总表](../../index/INDEX.md)
