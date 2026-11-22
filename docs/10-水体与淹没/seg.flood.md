# `seg.flood`

> 洪水淹没范围主入口；两次水体推理再相减

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:667`（19 行） |
| 相关性 | ★★★ |
| 可迁移性 | C（跨分辨率失效） |
| 依赖 | 模型 DPT（water）×2 |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Segment flood areas from pre/post disaster optical satellite images. Detects standing water and flooded regions. Spatial resolution: 0.5m-1.0m.

## 这个工具做什么

给它灾前、灾后两张光学影像，它先分别认出两期的水面，再相减，得到「新淹了哪里」。注意它给的是范围，不含水深。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `pre_image_path` | str | 是 | — | 灾前影像路径 |
| `post_image_path` | str | 是 | — | 灾后影像路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to binary flooding mask (255 = flooding) |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 DPT（water）×2
- 硬件：水体权重推两次；1024² 约 20.7 s（实测）
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_flood
import json

res = json.loads(seg_flood(pre_image_path="pre.tif", post_image_path="post.tif"))
print(res)
```

```json
{
  "name": "seg.flood",
  "arguments": {
    "pre_image_path": "pre.tif",
    "post_image_path": "post.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 洪水淹没范围主入口；两次水体推理再相减
- **可迁移性**：C（跨分辨率失效）
- 需要**灾前 + 灾后同一区域的两期影像**；只给单期时无法调用。水体权重在 10 m 输入上 IoU 0.107、83 景中 54 景零检出（训练于 0.5–1 m）。

## 已知坑与建议

- **坑**：内部两次 `_water_mask` 调用**不传参考栅格**，所以输出掩膜是 PNG、没有地理参考——下游算面积必须手动给 `pixel_size_m`。
- **建议**：灾前若处于枯水期，河滩与水库消落带会被判成「新增淹没」；反过来用（丰水期→枯水期）可算退水面积，那是旱情指标。

## 相关工具

- [`seg.reservoir`](seg.reservoir.md)
- [`ras.threshold`](../40-栅格分析/ras.threshold.md)
- [`ras.area`](../40-栅格分析/ras.area.md)

---

[← 返回 10-水体与淹没](README.md)　·　[工具总表](../../index/INDEX.md)
