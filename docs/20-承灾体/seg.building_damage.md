# `seg.building_damage`

> 淹没区房屋灾损统计

| | |
|---|---|
| 模块 | `perception` · `src/dora/tools/perception.py:256`（14 行） |
| 相关性 | ★★★ |
| 可迁移性 | B（≤1.6 m） |
| 依赖 | 模型 BitemporalDPT 6ch |
| 异常处理 | 函数内 `try/except`：异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Segment building damage from pre/post disaster optical satellite images. Uses difference-based detection to classify buildings into damage levels. Spatial resolution: 0.8m. The input pre and post image requires 3-bands.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `pre_image_path` | str | 是 | — | 灾前影像路径 |
| `post_image_path` | str | 是 | — | 灾后影像路径 |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `mask_path` | str | Path to the saved damage mask image |
| `classes` | dict | Mapping of class values to damage levels |

**落盘产物**：`mask_path`（位于 `--temp_dir` 下，文件名带 6 位哈希）

## 依赖与运行

- 依赖：模型 BitemporalDPT 6ch
- 硬件：20.9 s/MP（实测）；一景 12.8 km² 约 5.8 min
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.perception import seg_building_damage
import json

res = json.loads(seg_building_damage(pre_image_path="pre.tif", post_image_path="post.tif"))
print(res)
```

```json
{
  "name": "seg.building_damage",
  "arguments": {
    "pre_image_path": "pre.tif",
    "post_image_path": "post.tif"
  }
}
```

## 适用边界

- **相关性**：★★★ —— 淹没区房屋灾损统计
- **可迁移性**：B（≤1.6 m）
- 训练于 0.8 m；1.6 m 逐类 IoU 0.43–0.52、2.0 m 只能出「是否损毁」总量、3.2 m 中间档塌陷。

## 已知坑与建议

- **坑**：**16 位值域直接喂入会整幅全背景**（5 景中 4 景全空、1 景剩 281 px），且不报错。输入必须先拉回 0–255。
- **建议**：输出 0=背景、1=完好、2=部分损毁、3=完全损毁。大图会走 out-of-core；16 MP 以上建议自己先切片。

## 相关工具

- [`seg.road_damage`](seg.road_damage.md)
- [`ras.resample`](../40-栅格分析/ras.resample.md)
- [`vec.intersect`](../50-矢量与空间关系/vec.intersect.md)

---

[← 返回 20-承灾体](README.md)　·　[工具总表](../../index/INDEX.md)
