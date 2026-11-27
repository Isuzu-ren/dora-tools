# DORA 工具库 · 可读版

把 DORA 的 **108 件上游 MCP 工具**按功能域重新组织成一套中文说明，附一份与上游一致的代码副本；
另**新增 5 件地形工具**（`ras.terrain` / `ras.geomorphons` / `ras.flow` / `ras.catchment` / `ras.contour`），单独标注、不改上游任何一行。

> 上游项目：DORA: Can LLM Agents Respond to Disasters?（NeurIPS 2026）
> 本仓库只做「整理与说明」，**不改动工具实现**；代码位于 `src/`，与上游逐字一致。

## 三种看法

| 想做什么 | 入口 |
|---|---|
| 快速找工具 | 打开 [`index/index.html`](index/index.html)，按关键词或域筛选（双击即可，无需联网） |
| 看总表 | [`index/INDEX.md`](index/INDEX.md) —— 113 行，按域排序 |
| 读某件工具 | [`docs/`](docs/) —— 9 个功能域，每域一个 README + 每工具一页 |
| 看实际效果 | 每页的「示例」段：真实输入的预览图 + 工具原样返回的 JSON + 产物渲染 |

## 目录

```
src/dora/tools/        代码副本（6 个上游服务 + terrain.py 扩展 + 模型实现子包）
docs/                  说明文档
  00-快速开始.md
  01-工具全景.md        两种切法、相关性与可迁移性
  10-水体与淹没/        每域：README.md + 逐工具页
  ...
  99-附录/             接入红线、已知陷阱、评测摘要、术语
examples/              每件工具一组「真跑出来」的示例
  <域>/<工具>/         input.json（参数）+ output.json（返回）+ 渲染图 + meta.json
index/
  INDEX.md             113 件总表（108 上游 + 5 扩展）
  index.html           可搜索页面（单文件，无外部依赖）
  tools.json           机器可读（113 条，含参数与返回字段）
scripts/               提取、示例、生成、自检脚本
```

## 两个标签

每件工具都带两个标签，来自一周的真实评测（见 [`docs/99-附录/C-评测结论摘要.md`](docs/99-附录/C-评测结论摘要.md)）：

- **相关性**：与水旱预警业务的关系（★★★ 40 / ★★ 53 / ★ 10 / ○ 10）
- **可迁移性**：搬到新平台要付多少代价（A 直迁 81 / B 改造 11 / C 重训 11 / D 弃用 10）

两个维度交叉后最需要注意的一句：**★★★ 里必须重训的 4 件，恰好是滑坡、水库、洪水、航拍水体**
——也就是淹没范围、水域面积、滑坡这三个业务主指标。骨架能搬，感知要重训。

## 快速验证环境

```bash
pip install -e .
python scripts/smoke_test.py        # 造一张 64×64 栅格，跑通 阈值→面积
```

感知模型需要额外依赖与 12 GB 权重：

```bash
pip install -e ".[perception]"
```

## 本仓库不包含什么

- **模型权重**（12 GB）：放在 `$DORA_DATA/checkpoints/`，不进仓库
- **数据集与评测产物**：随 DORA 主仓库提供，不在本仓库
- **Agent 与评测框架**：`dora/agent`、`evaluation.py` 未复制，本仓库只有工具层

## 更新方式

1. 用上游最新代码覆盖 `src/dora/tools/`（**不要在副本里改代码**，否则与上游分叉）
2. `python scripts/extract_tools.py` —— 重新抽取全部工具的签名与说明
3. `python scripts/build_examples.py` —— 真跑一遍，重建 `examples/` 下的示例输入与输出
4. `python scripts/build_docs.py` —— 重建 docs/ 与 index/
5. 人工文案在 `scripts/content.py`（领域导语、逐工具补充、附录），重建时不会被覆盖

示例需要 `DORA_DATA` 指向的 DORA 数据根（影像 + 权重），没有数据时第 3 步会跳过对应工具，
页面上的「示例」段随之缺省，其余内容不受影响。

## 重新生成文档

```bash
python scripts/extract_tools.py     # 从源码提取 113 件 → index/tools.json
python scripts/build_docs.py        # 生成 docs/ 与 index/
python scripts/check_docs.py        # 自检：件数、参数一致性、死链
```
