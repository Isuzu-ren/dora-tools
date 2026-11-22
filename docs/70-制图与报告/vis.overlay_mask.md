# `vis.overlay_mask`

> 淹没范围图

| | |
|---|---|
| 模块 | `vis` · `src/dora/tools/vis.py:882`（11 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | PIL |
| 异常处理 | **无统一包装**：异常会直接抛出（MCP 层表现为 tool error） |

## 源码中的原话

> Overlay a segmentation mask on top of a base image. Inputs: - image_path: base raster image - mask_path: segmentation mask path - alpha: overlay opacity - class_labels: optional class label dict Output file is written to a managed location; its path is returned in the result dict as output_path.

## 这个工具做什么

把彩色范围半透明地压在卫星底图上，一眼看出「淹的是哪片地」。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `image_path` | str | 是 | — | 输入栅格路径（GeoTIFF / PNG；PNG 无地理参考） |
| `mask_path` | str | 是 | — | 掩膜路径（二值或多类） |
| `alpha` | float | 否 | `0.45` | 叠加透明度（0–1） |
| `class_labels` | dict[str,str]? | 否 | `None` | 类别值到名称的映射，用于图例 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `output_path` | str | 生成的图片路径（由调用方通过 `output_path` 参数指定） |

## 依赖与运行

- 依赖：PIL
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.vis import overlay_mask_tool
import json

res = json.loads(overlay_mask_tool(image_path="input.tif", mask_path="mask.png"))
print(res)
```

```json
{
  "name": "vis.overlay_mask",
  "arguments": {
    "image_path": "input.tif",
    "mask_path": "mask.png"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 淹没范围图
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 70-制图与报告](README.md)　·　[工具总表](../../index/INDEX.md)
