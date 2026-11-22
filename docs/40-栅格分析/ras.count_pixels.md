# `ras.count_pixels`

> 面积前的中间量

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:1116`（19 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | numpy |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Count pixels for specified classes in a mask image.

## 这个工具做什么

数一数某类区域占了多少个像素。面积就是它乘上每个像素代表的平方米数。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `mask_path` | str | 是 | — | 掩膜路径（二值或多类） |
| `classes` | list[int] | 是 | — | 要保留的类别值列表 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `counts` | dict | Pixel counts per class |
| `total` | int | Total pixel count for all specified classes |

## 依赖与运行

- 依赖：numpy
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import ras_count_pixels
import json

res = json.loads(ras_count_pixels(mask_path="mask.png", classes="input.tif"))
print(res)
```

```json
{
  "name": "ras.count_pixels",
  "arguments": {
    "mask_path": "mask.png",
    "classes": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★ —— 面积前的中间量
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 40-栅格分析](README.md)　·　[工具总表](../../index/INDEX.md)
