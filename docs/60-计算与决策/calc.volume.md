# `calc.volume`

> 蓄水量、土方量、淹没水量

| | |
|---|---|
| 模块 | `calculate` · `src/dora/tools/calculate.py:197`（17 行） |
| 相关性 | ★★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Calculate volume from area and depth. Volume = Area × Depth

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `area_m2` | float | 是 | — | Area in square meters |
| `depth_m` | float | 是 | — | Depth/height in meters |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `volume_m3` | float | Volume in cubic meters |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.calculate import calc_volume
import json

res = json.loads(calc_volume(area_m2="0.0", depth_m="0.0"))
print(res)
```

```json
{
  "name": "calc.volume",
  "arguments": {
    "area_m2": "0.0",
    "depth_m": "0.0"
  }
}
```

## 适用边界

- **相关性**：★★ —— 蓄水量、土方量、淹没水量
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 60-计算与决策](README.md)　·　[工具总表](../../index/INDEX.md)
