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

## 这个工具做什么

一次生成多层缓冲带，比如 100 / 500 / 1000 米三圈，用来分轻重影响区。

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

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：同目录 roads.geojson（193 条道路，已转 EPSG:6677）

```json
{
  "vector_path": "<work>/fixtures/roads.geojson",
  "meters": [
    20.0,
    40.0
  ]
}
```

### 示例输出

```json
{
  "tool": "vec.kbuffer",
  "buffers": [
    {
      "distance_input_m": 20.0,
      "distance_used_units": 20.0,
      "buffer_path": "<temp_dir>/buffer_20.0_3fcaa4.geojson"
    },
    {
      "distance_input_m": 40.0,
      "distance_used_units": 40.0,
      "buffer_path": "<temp_dir>/buffer_40.0_3fcaa4.geojson"
    }
  ],
  "input_vector": "<work>/fixtures/roads.geojson"
}
```

耗时 0.16 s（本机 8 核 CPU，无 GPU）。

## 适用边界

- **相关性**：★★ —— 分级影响区（100/500/1000 m）
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 50-矢量与空间关系](README.md)　·　[工具总表](../../index/INDEX.md)
