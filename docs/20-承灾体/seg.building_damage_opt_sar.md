# `seg.building_damage_opt_sar`

> 汛期多云雨，SAR 是唯一可靠手段

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:290`（14 行） |
| 相关性 | ★★★ |
| 可迁移性 | B（需 SAR 预处理） |
| 依赖 | 模型 BitemporalDPT 6ch |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Segment building damage from pre-disaster optical and post-disaster SAR satellite images. Uses difference-based detection to classify buildings into damage levels. Spatial resolution: 0.8m. The input pre and post image requires 3-bands.

## 这个工具做什么

灾前用光学、灾后用雷达，做同样的建筑损毁分级。专为汛期连阴雨、光学卫星拍不到的情况准备。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `pre_image_path` | str | 是 | — | 灾前影像路径 |
| `post_image_path` | str | 是 | — | 灾后影像路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to the saved damage mask image |
| `classes` | dict | Mapping of class values to damage levels |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 BitemporalDPT 6ch
- 硬件：需模型权重；CPU 可跑但慢（秒级/MP），建议 GPU（未实测）
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_building_damage_opt_sar
import json

res = json.loads(seg_building_damage_opt_sar(pre_image_path="pre.tif", post_image_path="post.tif"))
print(res)
```

```json
{
  "name": "seg.building_damage_opt_sar",
  "arguments": {
    "pre_image_path": "pre.tif",
    "post_image_path": "post.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 汛期多云雨，SAR 是唯一可靠手段
- **可迁移性**：B（需 SAR 预处理）
- 灾后必须是 SAR，且需先在工具外完成辐射定标、地理编码、斑点滤波。精度未实测（本地无真值）。

## 已知坑与建议

- **建议**：中国汛期主雨带云量高，光学连续多日不可用；这件是为那个场景准备的。

## 相关工具

- [`seg.building_damage`](seg.building_damage.md)
- [`ras.area`](../40-栅格分析/ras.area.md)

---

[← 返回 20-承灾体](README.md)　·　[工具总表](../../index/INDEX.md)
