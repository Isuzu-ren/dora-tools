# `logi.truck_trips`

> 物资/土方运输车次

| | |
|---|---|
| 模块 | `calculate` · `src/dora/tools/calculate.py:561`（20 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Calculate the number of truck trips needed to transport a given volume. Trips = ceil(Volume / Capacity)

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `volume_m3` | float | 是 | — | Total volume to transport in cubic meters |
| `capacity_m3` | float | 是 | — | Truck capacity in cubic meters |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `trips_required` | int | Number of truck trips needed |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.calculate import logi_truck_trips
import json

res = json.loads(logi_truck_trips(volume_m3="0.0", capacity_m3="0.0"))
print(res)
```

```json
{
  "name": "logi.truck_trips",
  "arguments": {
    "volume_m3": "0.0",
    "capacity_m3": "0.0"
  }
}
```

## 适用边界

- **相关性**：★★ —— 物资/土方运输车次
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 60-计算与决策](README.md)　·　[工具总表](../../index/INDEX.md)
