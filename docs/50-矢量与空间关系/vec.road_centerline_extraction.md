# `vec.road_centerline_extraction`

> 路网骨架，用于通行分析

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:2480`（40 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | skimage+geo |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Extract road centerlines directly from a road mask by skeletonizing and outputting centerlines as GeoJSON LineStrings. The caller must supply the class-id lists corresponding to intact vs damaged road pixels (look them up in the upstream segmentation tool's returned `classes` dict).

## 这个工具做什么

从道路范围图里抽出一条条中心线，把「一片路面」变成「可以走的线」。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `mask_path` | str | 是 | — | 掩膜路径（二值或多类） |
| `intact_classes` | list[int] | 否 | `None` | Class ids treated as intact road |
| `damaged_classes` | list[int] | 否 | `None` | Class ids treated as damaged road |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `centerline_path` | str | Path to centerline GeoJSON |

**落盘产物**：`centerline_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：skimage+geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import road_centerline_extraction
import json

res = json.loads(road_centerline_extraction(mask_path="mask.png"))
print(res)
```

```json
{
  "name": "vec.road_centerline_extraction",
  "arguments": {
    "mask_path": "mask.png"
  }
}
```

## 适用边界

- **相关性**：★★ —— 路网骨架，用于通行分析
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
