# `ras.resample`

> 统一 GSD：模型对分辨率敏感，这一步不能省

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:3693`（58 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | rasterio |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Resample a raster to a new pixel size. Useful for harmonizing resolution between multi-source data (e.g., resampling a coarser grid to a finer target resolution).

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `raster_path` | str | 是 | — | 栅格路径 |
| `target_pixel_size_m` | float | 是 | — | Desired pixel size in meters |
| `resampling` | str | 否 | `'bilinear'` | 重采样方法：nearest / bilinear / cubic |
| `out_path` | str? | 否 | `None` | 输出文件路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `output_path` | str | Path to the resampled raster |
| `src_pixel_size_m` | float | Original pixel size |
| `dst_pixel_size_m` | float | New pixel size |
| `shape` | list[int | [height, width] |

**落盘产物**：`output_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：rasterio
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import ras_resample
import json

res = json.loads(ras_resample(raster_path="input.tif", target_pixel_size_m="0.0"))
print(res)
```

```json
{
  "name": "ras.resample",
  "arguments": {
    "raster_path": "input.tif",
    "target_pixel_size_m": "0.0"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 统一 GSD：模型对分辨率敏感，这一步不能省
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

## 已知坑与建议

- **建议**：模型对分辨率敏感，接入前这一步不能省。降采样只改像素，不改类别语义——3.2 m 时「部分损毁」会塌得比「完全损毁」更快。

## 相关工具

- [`ras.reproject`](ras.reproject.md)
- [`seg.building_damage`](../20-承灾体/seg.building_damage.md)

---

[← 返回 40-栅格分析](README.md)　·　[工具总表](../../index/INDEX.md)
