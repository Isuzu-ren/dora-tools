# `seg.reservoir`

> 干旱核心：水域面积萎缩监测；需 14 波段输入

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:451`（13 行） |
| 相关性 | ★★★ |
| 可迁移性 | C（14 波段归一化） |
| 依赖 | 模型 WeTr 14ch |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Segment reservoirs from multi-modal data: multi-spectral optical + DEM + slope. Spatial resolution: 10m. IMPORTANT: The input image MUST have exactly 14 bands (12-band multi-spectral + DEM: 1 band + Slope: 1 band). If your data has separate multi-spectral, DEM, and slope files, use ras.concat to merge them first.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `post_image_path` | str | 是 | — | 灾后影像路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to the saved binary reservoir mask |
| `classes` | dict | Mapping of class values to semantic labels |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 WeTr 14ch
- 硬件：需 15 MB 权重；CPU 可跑，一景 2.66 MP 约 6 s
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_reservoir
import json

res = json.loads(seg_reservoir(post_image_path="post.tif"))
print(res)
```

```json
{
  "name": "seg.reservoir",
  "arguments": {
    "post_image_path": "post.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 干旱核心：水域面积萎缩监测；需 14 波段输入
- **可迁移性**：C（14 波段归一化）
- 必须 **14 波段且顺序固定**（B1–B12 + 坡度 + DEM），并带 Landslide4Sense 的归一化常量；换 GF 系列需重标定或重训。

## 已知坑与建议

- **坑**：波段对调**不报错**：DEM 与坡度互换后，同一景面积从 0.815 km² 变成 1.476 km²。

## 相关工具

- [`ras.concat`](../40-栅格分析/ras.concat.md)
- [`ras.resample`](../40-栅格分析/ras.resample.md)
- [`ras.area`](../40-栅格分析/ras.area.md)

---

[← 返回 10-水体与淹没](README.md)　·　[工具总表](../../index/INDEX.md)
