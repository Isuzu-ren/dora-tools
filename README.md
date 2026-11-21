# DORA 工具库 · 可读版

把 DORA 的 **108 件 MCP 工具**按功能域重新组织成一套中文说明，附一份与上游一致的代码副本。

> 上游项目：DORA: Can LLM Agents Respond to Disasters?（NeurIPS 2026）
> 本仓库只做「整理与说明」，**不改动工具实现**；代码位于 `src/`，与上游逐字一致。

## 三种看法

| 想做什么 | 入口 |
|---|---|
| 快速找工具 | 打开 [`index/index.html`](index/index.html)，按关键词或域筛选（双击即可，无需联网） |
| 看总表 | [`index/INDEX.md`](index/INDEX.md) —— 108 行，按域排序 |
| 读某件工具 | [`docs/`](docs/) —— 9 个功能域，每域一个 README + 每工具一页 |

## 目录

```
src/dora/tools/        代码副本（6 个服务模块 + 模型实现子包）
docs/                  说明文档
  00-快速开始.md
  01-工具全景.md        两种切法、相关性与可迁移性
  10-水体与淹没/        每域：README.md + 逐工具页
  ...
  99-附录/             接入红线、已知陷阱、评测摘要、术语
index/
  INDEX.md             108 件总表
  index.html           可搜索页面（单文件，无外部依赖）
  tools.json           机器可读（108 条，含参数与返回字段）
scripts/               提取、生成、自检脚本
```

## 两个标签

每件工具都带两个标签，来自一周的真实评测（见 [`docs/99-附录/C-评测结论摘要.md`](docs/99-附录/C-评测结论摘要.md)）：

- **相关性**：与水旱预警业务的关系（★★★ 36 / ★★ 52 / ★ 10 / ○ 10）
- **可迁移性**：搬到新平台要付多少代价（A 直迁 76 / B 改造 11 / C 重训 11 / D 弃用 10）

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
- **数据集与评测产物**：在 DORA 主仓库
- **Agent 与评测框架**：`dora/agent`、`evaluation.py` 未复制，本仓库只有工具层

## 更新方式

1. 用上游最新代码覆盖 `src/dora/tools/`（**不要在副本里改代码**，否则与上游分叉）
2. `python scripts/extract_tools.py` —— 重新抽取 108 件的签名与说明
3. `python scripts/build_docs.py` —— 重建 docs/ 与 index/
4. 人工文案在 `scripts/content.py`（领域导语、逐工具补充、附录），重建时不会被覆盖

## 本仓库不包含什么

- **模型权重**（12 GB）：放在 `$DORA_DATA/checkpoints/`，不进仓库
- **数据集与评测产物**：在 DORA 主仓库
- **Agent 与评测框架**：`dora/agent`、`evaluation.py` 未复制，本仓库只有工具层

## 更新方式

1. 用上游最新代码覆盖 `src/dora/tools/`（**不要在副本里改代码**，否则与上游分叉）
2. `python scripts/extract_tools.py` —— 重新抽取 108 件的签名与说明
3. `python scripts/build_docs.py` —— 重建 docs/ 与 index/
4. 人工文案在 `scripts/content.py`（领域导语、逐工具补充、附录），重建时不会被覆盖

## 重新生成文档

```bash
python scripts/extract_tools.py     # 从源码提取 108 件 → index/tools.json
python scripts/build_docs.py        # 生成 docs/ 与 index/
python scripts/check_docs.py        # 自检：件数、参数一致性、死链
```
