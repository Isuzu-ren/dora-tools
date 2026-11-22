# `seg.building_lowres`

> 大范围承灾体底数（PlanetScope）

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:731`（39 行） |
| 相关性 | ★★ |
| 可迁移性 | B（3.46 m 专用） |
| 依赖 | 模型 HRNetSeg |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Segment building areas from single temporal low-resolution optical satellite image. Spatial resolution: 3.46m.

## 这个工具做什么

在比较粗糙（约 3 米）的影像上把建筑物轮廓找出来，用于大范围摸底，不求精细。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `image_path` | str | 是 | — | 输入栅格路径（GeoTIFF / PNG；PNG 无地理参考） |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to binary building mask (255 = building) |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 HRNetSeg
- 硬件：71.2 s/MP（实测）；512² 约 5.5 GB 内存
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_building_lowres
import json

res = json.loads(seg_building_lowres(image_path="input.tif"))
print(res)
```

```json
{
  "name": "seg.building_lowres",
  "arguments": {
    "image_path": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★ —— 大范围承灾体底数（PlanetScope）
- **可迁移性**：B（3.46 m 专用）
- 3.46 m 专用（PlanetScope 一类），用于大范围承灾体底数。**71.2 s/MP**，512² 需约 5.5 GB 内存，16 MP 以上会 OOM。

## 相关工具

- [`ras.resample`](../40-栅格分析/ras.resample.md)
- [`vec.intersect`](../50-矢量与空间关系/vec.intersect.md)

---

[← 返回 20-承灾体](README.md)　·　[工具总表](../../index/INDEX.md)
