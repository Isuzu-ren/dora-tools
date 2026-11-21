# `vec.kbuffer`

> 分级影响区（100/500/1000 m）

| | |
|---|---|
| 模块 | `analysis` · `src/dora/tools/analysis.py:2411`（36 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | geo |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Create multiple buffers for given distances around geometries in a vector file. The distances are interpreted in CRS units (meters if CRS is metric).

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `vector_path` | str | 是 | — | 矢量路径（GeoJSON） |
| `meters` | list[float] | 是 | — | Distances for buffering |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `buffers` | list | List of {distance, buffer_path} |

## 依赖与运行

- 依赖：geo
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.analysis import vec_kbuffer
import json

res = json.loads(vec_kbuffer(vector_path="admin.geojson", meters="input.tif"))
print(res)
```

```json
{
  "name": "vec.kbuffer",
  "arguments": {
    "vector_path": "admin.geojson",
    "meters": "input.tif"
  }
}
```

## 适用边界

- **相关性**：★★ —— 分级影响区（100/500/1000 m）
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
