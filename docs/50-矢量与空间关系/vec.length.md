# `vec.length`

> 河道长度、道路淹没长度

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:2798`（25 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Compute total length (m) for LineString features.

## 这个工具做什么

量线有多长。河道多长、被淹的路段多长，都是它算。

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_path` | str | 是 | — | 矢量路径（GeoJSON） |
| `pixel_size_m` | float | 否 | `None` | 像元边长（米）。掩膜无地理参考时必须显式给出 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `table_path` | str | CSV with {id, length_m} |

**落盘产物**：`table_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_length
import json

res = json.loads(vec_length(vector_path="admin.geojson"))
print(res)
```

```json
{
  "name": "vec.length",
  "arguments": {
    "vector_path": "admin.geojson"
  }
}
```

## 适用边界

- **相关性**：★★ —— 河道长度、道路淹没长度
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
