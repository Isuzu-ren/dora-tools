# `vec.dissolve`

> 把破碎淹没斑块合成连片淹没区

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:3992`（26 行） |
| 相关性 | ★★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Dissolve (merge) overlapping or adjacent polygons into larger ones, optionally grouping by an attribute field. Useful for consolidating fragmented damage patches into contiguous impact zones.

## 这个工具做什么

把挨在一起的碎块合并成整片。淹没区原本是几十个小斑块，合并后才是「一片洪区」。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_path` | str | 是 | — | 矢量路径（GeoJSON） |
| `by` | str? | 否 | `None` | Attribute field to group by before dissolving |
| `out_path` | str? | 否 | `None` | 输出文件路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `output_path` | str | Path to dissolved GeoJSON |
| `input_count` | int | Number of input features |
| `output_count` | int | Number of features after dissolve |

**落盘产物**：`output_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_dissolve
import json

res = json.loads(vec_dissolve(vector_path="admin.geojson"))
print(res)
```

```json
{
  "name": "vec.dissolve",
  "arguments": {
    "vector_path": "admin.geojson"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 把破碎淹没斑块合成连片淹没区
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
