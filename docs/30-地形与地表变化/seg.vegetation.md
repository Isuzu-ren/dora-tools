# `seg.vegetation`

> 旱情：植被覆盖变化、受旱耕地识别

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:700`（18 行） |
| 相关性 | ★★★ |
| 可迁移性 | B（仅单期） |
| 依赖 | 模型 DPT-landcover |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Segment vegetation areas from single temporal optical satellite image. Detects trees, shrub and agriculture land. Spatial resolution: 0.5m-1.0m.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `image_path` | str | 是 | — | 输入栅格路径（GeoTIFF / PNG；PNG 无地理参考） |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to binary vegetation mask (255 = vegetation) |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 DPT-landcover
- 硬件：12.2 s/MP（实测）；一景 12.8 km² 约 3.4 min
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_vegetation
import json

res = json.loads(seg_vegetation(image_path="input.tif"))
print(res)
```

```json
{
  "name": "seg.vegetation",
  "arguments": {
    "image_path": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 旱情：植被覆盖变化、受旱耕地识别
- **可迁移性**：B（仅单期）
- **只做单期**。两期相减的平均面积变化 37.4%、一致率低至 0.63，会把模型漂移当成灾损变化。

## 已知坑与建议

- **坑**：文档说取第 5/6 类，实际输出是 **0/255 二值掩膜**（`_binary_mask` 的合并结果），统计时按「>0」计数。

## 相关工具

- [`ras.area`](../40-栅格分析/ras.area.md)
- [`vis.temporal_panel`](../70-制图与报告/vis.temporal_panel.md)

---

[← 返回 30-地形与地表变化](README.md)　·　[工具总表](../../index/INDEX.md)
