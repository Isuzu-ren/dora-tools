#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成 docs/ 下的领域 README、逐工具页面，以及 index/ 下的总表与可搜索页面。

    python scripts/build_docs.py

数据来源：index/tools.json（由 scripts/extract_tools.py 生成）+ scripts/content.py（人工文案）。
每次运行全量重建 docs/ 与 index/index.html，可反复执行。
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import content  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX = ROOT / "index"
TOOLS_JSON = INDEX / "tools.json"

REL_ORDER = {"★★★": 0, "★★": 1, "★": 2, "○": 3}

DOMAIN_NEIGHBORS = {
    "water": ["`ras.threshold`（40-栅格分析）：SAR 阈值法，零权重基线",
              "`ras.area` / `calc.volume`（40 / 60）：面积与蓄水量",
              "`vis.overlay_mask`（70-制图与报告）：淹没范围压底图"],
    "asset": ["`ras.resample`（40-栅格分析）：先把分辨率统一到 ≤1.6 m",
              "`vec.intersect`（50-矢量与空间关系）：损毁图斑叠行政区/居民地",
              "`vec.road_centerline_extraction` → `vec.build_graph`（50）：通行阻断分析"],
    "terrain": ["`ras.diff`（40-栅格分析）：两期 DEM 相减求高程变化",
                "`ras.focal_stats`（40）：地形粗糙度",
                "`ras.threshold` + `ras.area`：变化超阈值区 → 面积"],
    "raster": ["`vec.raster_stats`（50-矢量与空间关系）：按行政区/流域汇总",
               "`tool.loop`（60-计算与决策）：按网格批量算",
               "`ras.vectorize` → `vis.damage_map`（70）：出图链路"],
    "vector": ["`ras.vectorize`（40-栅格分析）：掩膜转矢量是多数矢量流程的入口",
               "`poi.*`（80-POI-点位）：点位落进面内",
               "`vis.route_map`（70）：把路径画到底图上"],
    "compute": ["`ras.area` / `ras.count_pixels`（40 / 60）：本域多数输入的来源",
                "`tool.chart_data` → `vis.bar_chart`（70）：结果出图",
                "`logi.priority_score` → `poi.damage_population_exposure`（80）：处置排序"],
    "carto": ["`ras.vectorize`（40）：先矢量化再出专题图，边界更干净",
              "`tool.chart_data`（60）：图表的输入格式",
              "`report.extract_evidence`：出报告前的证据汇总"],
    "poi": ["`poi.world_to_pixel`：把业务点位对齐到影像",
            "`poi.filter_by_damage`：筛出位于受损建筑内的点",
            "`logi.priority_score`（60）：按人口/损失排序"],
    "other": ["与本项目无关，仅在特定子场景下可能有意义（如台风后的河道行洪障碍）。"],
}

TYPE_DEFAULT = {"str": '"input.tif"', "int": "1", "float": "0.0",
                "bool": "True", "list": "[]", "dict": "{}"}


# ---------------------------------------------------------------- 解析说明文字
def parse_sections(desc: str) -> dict:
    out = {"desc": [], "params": [], "returns": []}
    cur = "desc"
    for raw in (desc or "").splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.lower().startswith("description"):
            cur = "desc"
            continue
        if s.lower() in ("parameters:", "parameters", "params:"):
            cur = "params"
            continue
        if s.lower() in ("returns:", "return:", "returns"):
            cur = "returns"
            continue
        m = re.match(r"^[-*]\s*(.+)$", s)
        if m and cur in ("params", "returns"):
            out[cur].append(parse_item(m.group(1)))
        elif cur == "desc":
            out["desc"].append(s)
    return out


def parse_item(s: str) -> dict:
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)\s*:\s*(.*)$", s)
    if m:
        return {"name": m.group(1), "type": m.group(2), "desc": m.group(3).strip()}
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", s)
    if m:
        return {"name": m.group(1), "type": "", "desc": m.group(2).strip()}
    return {"name": "", "type": "", "desc": s}


TYPE_ALIAS = {
    "ListDict": "list[dict]", "ListDictStrAny": "list[dict]", "ListDictStrInt": "list[dict]",
    "OptListDict": "list[dict]?", "OptListDictStrAny": "list[dict]?",
    "OptListStr": "list[str]?", "OptListInt": "list[int]?",
    "ListStr": "list[str]", "ListFloat": "list[float]", "ListInt": "list[int]",
    "ListListInt": "list[list[int]]", "ListLoopItem": "list",
    "DictStrFloat": "dict[str,float]", "DictStrStr": "dict[str,str]",
    "OptDictStrStr": "dict[str,str]?", "OptDictStrAny": "dict?",
    "ListOrDictStrAny": "list | dict",
    "Optional[str]": "str?", "Optional[int]": "int?", "Optional[float]": "float?",
    "Optional[Union[str, int]]": "str | int?",
}

HW = {
    "seg.landslide_ms": "2.7 s/MP（实测）；一景 12.8 km² 约 0.75 min",
    "seg.vegetation": "12.2 s/MP（实测）；一景 12.8 km² 约 3.4 min",
    "seg.building_damage": "20.9 s/MP（实测）；一景 12.8 km² 约 5.8 min",
    "seg.building_lowres": "71.2 s/MP（实测）；512² 约 5.5 GB 内存",
    "seg.flood": "水体权重推两次；1024² 约 20.7 s（实测）",
    "seg.road_damage": "BitemporalDPT；1024² 约 30–100 s（实测）",
}


def short_type(t: str | None) -> str:
    if not t:
        return "—"
    t = t.replace("typing.", "")
    return TYPE_ALIAS.get(t, t.replace("Optional[", "").rstrip("]"))


def esc(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def guard_text(t: dict) -> str:
    if t.get("guarded"):
        return "有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{\"error\": ...}` 返回"
    if t.get("has_try"):
        return "函数内 `try/except`：异常转成 `{\"error\": ...}` 返回"
    return "**无统一包装**：异常会直接抛出（MCP 层表现为 tool error）"


def hardware(t: dict) -> str:
    if t["name"] in HW:
        return HW[t["name"]]
    dep = t.get("dep") or ""
    if t["transfer"].startswith("A"):
        return "纯算法，CPU 毫秒级；无需 GPU"
    if "14ch" in dep:
        return "需 15 MB 权重；CPU 可跑，一景 2.66 MP 约 6 s"
    if "HRNet" in dep:
        return "需 264 MB 权重；**71.2 s/MP**，512² 约 5.5 GB 内存"
    if "LLM" in dep:
        return "需外部 LLM 接口；耗时取决于服务端"
    return "需模型权重；CPU 可跑但慢（秒级/MP），建议 GPU（未实测）"


def example_args(t: dict) -> dict:
    args = {}
    for p in t["params"]:
        if not p["required"]:
            continue
        name = p["name"]
        typ = short_type(p["type"])
        if "path" in name:
            if "vector" in name or "geojson" in name:
                args[name] = "admin.geojson"
            elif "mask" in name:
                args[name] = "mask.png"
            elif "dem" in name:
                args[name] = "dem.tif"
            elif "pre" in name:
                args[name] = "pre.tif"
            elif "post" in name:
                args[name] = "post.tif"
            elif "pre" in name:
                args[name] = "pre.tif"
            elif "post" in name:
                args[name] = "post.tif"
            else:
                args[name] = "input.tif"
        elif typ in TYPE_DEFAULT:
            args[name] = TYPE_DEFAULT[typ]
        else:
            args[name] = "input.tif"
    return args


def py_repr(v) -> str:
    if isinstance(v, str):
        return f'"{v}"'
    if isinstance(v, bool):
        return "True" if v else "False"
    return repr(v)


# ---------------------------------------------------------------- 组装记录
def enrich(tools: list[dict]) -> list[dict]:
    out = []
    for t in tools:
        sec = parse_sections(t["docstring"])
        pdesc = {p["name"]: p["desc"] for p in sec["params"] if p["name"]}
        rdesc = {p["name"]: (p["type"], p["desc"]) for p in sec["returns"] if p["name"]}

        params = []
        for p in t["params"]:
            note = content.PARAM_HINTS.get(p["name"]) or pdesc.get(p["name"], "")
            params.append({**p, "desc": note})

        returns = [{"name": k, "type": short_type(v[0]), "desc": v[1]}
                   for k, v in rdesc.items()]

        note = content.NOTES.get(t["name"], {})
        t2 = dict(t)
        t2.update({
            "desc_cn": t.get("usage") or "",
            "desc_raw": " ".join(sec["desc"])[:600],
            "params_doc": params,
            "returns_doc": returns,
            "boundary": note.get("boundary", ""),
            "pitfall": note.get("pitfall", ""),
            "tip": note.get("tip", ""),
            "related": note.get("related", []),
        })
        out.append(t2)
    return out


# ---------------------------------------------------------------- 渲染
def fallback_boundary(t: dict) -> str:
    lv = (t["transfer"] or "A")[0]
    if t["relevance"] == "○":
        return "与本项目无交集，仅为台账完整而保留。"
    return {
        "A": "纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。",
        "B": "有权重、域内可用，但必须守住三条红线；本件未做专项实测，接入前请目视复核 10–20 景。",
        "C": "输入契约与新数据不兼容，直接推会静默失效；本件未做专项实测，判断依据是代码契约（波段 / 视角 / 分辨率）。",
        "D": "业务上不需要迁移。",
    }.get(lv, "")


def render_example(t: dict, folder: str) -> list[str]:
    """「示例输入 / 示例输出」两段，内容全部来自 examples/ 下真实运行留下的文件。"""
    ex = ROOT / "examples" / folder / t["name"]
    meta_p = ex / "meta.json"
    if not meta_p.exists():
        return []
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    args = json.loads((ex / "input.json").read_text(encoding="utf-8"))
    resp = json.loads((ex / "output.json").read_text(encoding="utf-8"))
    rel = f"../../examples/{folder}/{t['name']}"
    status = meta.get("status", "real")
    secs = ["## 示例", ""]
    if status == "constructed":
        secs.append("> ⚠️ **构造示意（未实际运行）**：本机缺少该工具所需的外部服务（如 GPT 接口），"
                    "下面的返回按源码的字段结构手写，仅用于说明「它会返回什么」。")
    elif status == "demo":
        secs.append("> ⚠️ **示意输入**：工具确实运行了，但输入与本工具的适用场景不完全对应"
                    "（如用建筑影像演示滑坡双时相模型），结果只说明「接口怎么用」，不代表精度。")
    else:
        secs.append("> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。"
                    "路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。")
    secs.append("")

    secs += ["### 示例输入", ""]
    if meta.get("inputs"):
        secs.append("数据：" + "；".join(meta["inputs"]))
        secs.append("")
    secs += ["```json", json.dumps(args, ensure_ascii=False, indent=2), "```", ""]
    if meta.get("figures", {}).get("in"):
        secs += [f"[![示例输入]({rel}/in.webp)]({rel}/in.webp)", ""]

    secs += ["### 示例输出", ""]
    secs += ["```json", json.dumps(resp, ensure_ascii=False, indent=2), "```", ""]
    figs = meta.get("figures", {})
    out_key = next((k for k in ("out", "mask") if k in figs), None)
    if out_key:
        cap = meta.get("caption") or "示例输出"
        secs += [f"[![{cap}]({rel}/{figs[out_key]})]({rel}/{figs[out_key]})", "",
                 f"*{cap}*（点击图片看原图）", ""]
    if meta.get("note"):
        secs += [f"> {meta['note']}", ""]
    wall = meta.get("wall_time_s")
    if wall:
        secs += [f"耗时 {wall} s（本机 8 核 CPU，无 GPU）。", ""]
    return secs


def render_tool(t: dict, folder: str, folder_by_tool: dict | None = None) -> str:
    lines = [f"# `{t['name']}`", ""]
    if t.get("origin") == "extension":
        lines += ["> ★ **本地扩展**：本件不在上游 DORA 的 108 件之内，由本仓库新增"
                  "（`src/dora/tools/terrain.py`），实现依据见页末「已知坑」。", ""]
    if t["relevance"] in ("○", "★") and t["domain"] == "other":
        lines += ["> **与本项目无关**：本件不在水旱预警链路上，保留仅为台账完整（108 件与上游一致）。", ""]
    if t["desc_cn"]:
        lines += [f"> {t['desc_cn']}", ""]

    lines += ["| | |", "|---|---|",
              f"| 模块 | `{t['module']}` · `{t['source']}:{t['lineno']}`（{t['loc']} 行） |",
              f"| 相关性 | {t['relevance']} |",
              f"| 可迁移性 | {t['transfer']} |",
              f"| 依赖 | {t['dep']} |",
              f"| 异常处理 | {guard_text(t)} |",
              ""]

    if t["desc_raw"] and t["desc_raw"] != t["desc_cn"]:
        lines += ["## 源码中的原话", "", f"> {t['desc_raw']}", ""]

    plain = content.PLAIN.get(t["name"])
    if plain:
        lines += ["## 这个工具做什么", "", plain, ""]

    lines += ["## 输入", ""]
    if t["params_doc"]:
        lines += ["| 参数 | 类型 | 必填 | 默认 | 说明 |", "|---|---|:-:|---|---|"]
        for p in t["params_doc"]:
            lines.append(f"| `{p['name']}` | {short_type(p['type'])} | {'是' if p['required'] else '否'} "
                         f"| {('`' + p['default'] + '`') if p['default'] else '—'} | {esc(p['desc']) or '—'} |")
    else:
        lines.append("无参数。")
    lines.append("")

    lines += ["## 输出", ""]
    if t["returns_doc"]:
        lines += ["| 字段 | 类型 | 说明 |", "|---|---|---|"]
        for r in t["returns_doc"]:
            lines.append(f"| `{r['name']}` | {r['type']} | {esc(r['desc']) or '—'} |")
    else:
        if t.get("artifacts"):
            lines += ["| 字段 | 类型 | 说明 |", "|---|---|---|"]
            for a in t["artifacts"]:
                lines.append(f"| `{a}` | str | 产物路径 |")
        elif t["module"] == "vis":
            lines += ["| 字段 | 类型 | 说明 |", "|---|---|---|",
                      "| `output_path` | str | 生成的图片路径（由调用方通过 `output_path` 参数指定） |"]
        elif t["module"] == "calculate":
            lines.append("返回 JSON 标量结果（如 `area_m2` / `score` / `volume`），**不产生文件产物**。")
        else:
            lines.append("返回 JSON 字符串，字段见源码。")
    paths = [r["name"] for r in t["returns_doc"] if r["name"].endswith("_path")]
    if paths:
        lines += ["", f"**落盘产物**：`{'`、`'.join(paths)}`（位于 `--temp_dir` 下，文件名带 6 位哈希）"]
    lines.append("")

    lines += ["## 依赖与运行", "",
              f"- 依赖：{t['dep']}",
              f"- 硬件：{hardware(t)}",
              "- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON", ""]

    args = example_args(t)
    kw = ", ".join(f"{k}={py_repr(v)}" for k, v in args.items())
    lines += ["## 调用", "", "```python",
              f"from dora.tools.{t['module']} import {t['func']}",
              "import json",
              "",
              f"res = json.loads({t['func']}({kw}))",
              "print(res)",
              "```", "",
              "```json",
              json.dumps({"name": t["name"], "arguments": args}, ensure_ascii=False, indent=2),
              "```", ""]

    lines += render_example(t, folder)

    lines += ["## 适用边界", ""]
    lines.append(f"- **相关性**：{t['relevance']} —— {t['desc_cn']}")
    lines.append(f"- **可迁移性**：{t['transfer']}")
    if t["boundary"]:
        lines.append(f"- {t['boundary']}")
    else:
        lines.append(f"- {fallback_boundary(t)}")
        if t["domain"] in content.DOMAIN_TABLES:
            lines.append("- 本域统一的输入口径（分辨率 / 时相 / 是否实测）见 "
                         "[README 的「实测口径」表](README.md#实测口径)")
    lines.append("")

    if t["pitfall"] or t["tip"]:
        lines += ["## 已知坑与建议", ""]
        if t["pitfall"]:
            lines.append(f"- **坑**：{t['pitfall']}")
        if t["tip"]:
            lines.append(f"- **建议**：{t['tip']}")
        lines.append("")

    if t["related"]:
        lines += ["## 相关工具", ""]
        for r in t["related"]:
            m = re.match(r"`([^`]+)`(.*)", r)
            name, tail = (m.group(1), m.group(2)) if m else (r, "")
            tail = re.sub(r"^（[^）]*）", "", tail)
            f2 = (folder_by_tool or {}).get(name)
            rel = f"{name}.md" if f2 in (None, folder) else f"../{f2}/{name}.md"
            lines.append(f"- [`{name}`]({rel}){tail}")
        lines.append("")

    lines += ["---", "",
              f"[← 返回 {folder}](README.md)　·　[工具总表](../../index/INDEX.md)", ""]
    return "\n".join(lines)


def render_domain(key: str, folder: str, tools: list[dict]) -> str:
    lines = [f"# {folder}", "", content.DOMAIN_INTRO[key].strip(), ""]
    if key in content.DOMAIN_TABLES:
        lines += [content.DOMAIN_TABLES[key].strip(), ""]
    lines += [f"## 工具速查（{len(tools)} 件）", "",
              "| 工具 | 相关性 | 可迁移性 | 用途 |", "|---|---|---|---|"]
    for t in sorted(tools, key=lambda x: (REL_ORDER.get(x["relevance"], 9), x["name"])):
        lines.append(f"| [`{t['name']}`]({t['name']}.md) | {t['relevance']} | {t['transfer']} | {esc(t['desc_cn'])} |")
    lines += ["", "## 相关但不在本域", ""]
    for n in DOMAIN_NEIGHBORS.get(key, []):
        lines.append(f"- {n}")
    lines += ["", "## 列的含义", "",
              "- **相关性**：★★★ 业务直接调用 / ★★ 流程必需 / ★ 特定子场景 / ○ 无交集",
              "- **可迁移性**：A 零改造直迁 / B 加规范可用 / C 必须重训 / D 不建议迁",
              "- 判定依据见 [`01-工具全景`](../01-工具全景.md) 与 [`99-附录/A-接入红线`](../99-附录/A-接入红线.md)", ""]
    return "\n".join(lines)


def render_index_md(tools: list[dict]) -> str:
    n_ext = sum(1 for t in tools if t.get("origin") == "extension")
    lines = [f"# {len(tools)} 件工具总表", "",
             f"其中上游 DORA {len(tools) - n_ext} 件，本仓库新增 {n_ext} 件（标 ★）。",
             "按功能域排序。完整字段见 `index/tools.json`，可交互版本见 `index/index.html`。", "",
             "| # | 域 | 工具 | 相关性 | 可迁移性 | 用途 |", "|---:|---|---|---|---|---|"]
    folder_of = dict(content.DOMAINS)
    for i, t in enumerate(tools, 1):
        mark = " ★" if t.get("origin") == "extension" else ""
        lines.append(f"| {i} | {folder_of[t['domain']]} | [`{t['name']}`](../docs/{folder_of[t['domain']]}/{t['name']}.md){mark} "
                     f"| {t['relevance']} | {t['transfer']} | {esc(t['desc_cn'])} |")
    return "\n".join(lines) + "\n"


HTML_TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>DORA 工具库 · {n_total} 件</title>
<style>
  :root {{ --bd:#d8dee6; --fg:#1f2328; --mut:#5b6673; --bg:#fbfcfd; --hl:#0b5cad; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font:14px/1.6 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif; color:var(--fg); background:var(--bg); }}
  header {{ padding:18px 24px 10px; border-bottom:1px solid var(--bd); background:#fff; position:sticky; top:0; z-index:5; }}
  h1 {{ margin:0 0 8px; font-size:20px; }}
  .bar {{ display:flex; gap:10px; flex-wrap:wrap; align-items:center; }}
  input[type=search] {{ flex:1 1 260px; padding:7px 10px; border:1px solid var(--bd); border-radius:6px; font-size:14px; }}
  select {{ padding:7px 8px; border:1px solid var(--bd); border-radius:6px; background:#fff; }}
  .stat {{ color:var(--mut); font-size:12px; margin-left:auto; }}
  main {{ display:grid; grid-template-columns:minmax(320px,38%) 1fr; gap:0; height:calc(100vh - 96px); }}
  .list {{ overflow:auto; border-right:1px solid var(--bd); background:#fff; }}
  .item {{ padding:9px 14px; border-bottom:1px solid #eef1f4; cursor:pointer; }}
  .item:hover {{ background:#f3f7fb; }}
  .item.on {{ background:#e8f1fb; box-shadow:inset 3px 0 0 var(--hl); }}
  .nm {{ font-family:ui-monospace,Consolas,monospace; font-size:13px; color:var(--hl); }}
  .meta {{ color:var(--mut); font-size:12px; }}
  .detail {{ overflow:auto; padding:22px 28px; }}
  h2 {{ font-size:19px; margin:0 0 4px; font-family:ui-monospace,Consolas,monospace; }}
  .tag {{ display:inline-block; padding:1px 7px; margin-right:6px; border-radius:10px; font-size:12px; background:#eef1f4; }}
  table {{ border-collapse:collapse; width:100%; margin:10px 0 18px; }}
  th,td {{ border:1px solid var(--bd); padding:5px 8px; text-align:left; vertical-align:top; }}
  th {{ background:#f5f7f9; font-weight:600; }}
  code {{ background:#f2f4f7; padding:1px 4px; border-radius:3px; font-family:ui-monospace,Consolas,monospace; }}
  pre {{ background:#1e2228; color:#e6edf3; padding:12px; border-radius:8px; overflow:auto; }}
  pre code {{ background:none; color:inherit; }}
  figure {{ margin:14px 0; }}
  figure img {{ max-width:100%; border:1px solid var(--line); border-radius:6px; display:block; cursor:zoom-in; }}
  #lb {{ position:fixed; inset:0; background:rgba(12,14,18,.88); display:none; z-index:99; }}
  #lb.on {{ display:block; }}
  #lb .canvas {{ position:absolute; inset:0; overflow:hidden; cursor:grab; }}
  #lb .canvas.drag {{ cursor:grabbing; }}
  #lb img {{ position:absolute; left:50%; top:50%; transform-origin:center; user-select:none; -webkit-user-drag:none; }}
  #lb .tools {{ position:absolute; top:14px; right:16px; display:flex; gap:6px; z-index:2; }}
  #lb button {{ background:rgba(255,255,255,.92); border:0; border-radius:6px; width:36px; height:34px;
                font-size:16px; cursor:pointer; color:#1e2228; }}
  #lb button:hover {{ background:#fff; }}
  #lb .cap {{ position:absolute; left:16px; bottom:14px; right:16px; color:#dfe6ee; font-size:13px; }}
  #lb .hint {{ position:absolute; left:16px; top:16px; color:#9fb0c2; font-size:12px; }}
  figcaption {{ font-size:12px; color:var(--dim); margin-top:6px; }}
  .dim {{ color:var(--dim); font-size:13px; }}
  h3 {{ font-size:14px; margin:18px 0 6px; color:var(--mut); }}
  .empty {{ color:var(--mut); padding:30px; }}
</style>
</head>
<body>
<header>
  <h1>DORA 工具库 · {n_total} 件</h1>
  <div class="bar">
    <input id="q" type="search" placeholder="搜索工具名、用途、参数…（如 淹没 / buffer / 面积）" autofocus>
    <select id="dom">{options}</select>
    <span class="stat" id="stat"></span>
  </div>
</header>
<main>
  <div class="list" id="list"></div>
  <div class="detail" id="detail"><div class="empty">左侧选一件工具查看详情。</div></div>
</main>
<div id="lb">
  <div class="hint">滚轮缩放 · 拖动平移 · 双击复位 · Esc 关闭</div>
  <div class="tools">
    <button id="lbOut" title="缩小">−</button>
    <button id="lbIn" title="放大">＋</button>
    <button id="lbReset" title="复位">1:1</button>
    <button id="lbClose" title="关闭">✕</button>
  </div>
  <div class="canvas" id="lbCanvas"><img id="lbImg" alt=""></div>
  <div class="cap" id="lbCap"></div>
</div>
<script>
const DATA = {data};
// ---- 图片灯箱：点击放大，滚轮/按钮缩放，拖动平移 ----
let lbScale = 1, lbX = 0, lbY = 0, lbDrag = null;
function lbApply() {{
  const img = document.getElementById('lbImg');
  img.style.transform = `translate(-50%,-50%) translate(${{lbX}}px,${{lbY}}px) scale(${{lbScale}})`;
}}
function openLB(el) {{
  const lb = document.getElementById('lb');
  document.getElementById('lbImg').src = el.src;
  document.getElementById('lbCap').textContent = (el.nextElementSibling && el.nextElementSibling.textContent) || el.alt || '';
  lbScale = 1; lbX = 0; lbY = 0; lbApply();
  lb.classList.add('on');
}}
function closeLB() {{ document.getElementById('lb').classList.remove('on'); }}
function zoomBy(f) {{ lbScale = Math.min(8, Math.max(0.2, lbScale * f)); lbApply(); }}
document.getElementById('lbClose').onclick = closeLB;
document.getElementById('lbIn').onclick = () => zoomBy(1.25);
document.getElementById('lbOut').onclick = () => zoomBy(0.8);
document.getElementById('lbReset').onclick = () => {{ lbScale = 1; lbX = 0; lbY = 0; lbApply(); }};
document.getElementById('lb').addEventListener('wheel', e => {{ e.preventDefault(); zoomBy(e.deltaY < 0 ? 1.12 : 0.9); }}, {{passive:false}});
document.getElementById('lbCanvas').addEventListener('dblclick', () => {{ lbScale = 1; lbX = 0; lbY = 0; lbApply(); }});
const lbCanvas = document.getElementById('lbCanvas');
lbCanvas.addEventListener('mousedown', e => {{ lbDrag = [e.clientX - lbX, e.clientY - lbY]; lbCanvas.classList.add('drag'); }});
window.addEventListener('mousemove', e => {{ if (lbDrag) {{ lbX = e.clientX - lbDrag[0]; lbY = e.clientY - lbDrag[1]; lbApply(); }} }});
window.addEventListener('mouseup', () => {{ lbDrag = null; lbCanvas.classList.remove('drag'); }});
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeLB(); }});
document.getElementById('lb').addEventListener('click', e => {{ if (e.target.id === 'lb' || e.target.id === 'lbCanvas') closeLB(); }});
const DOMAINS = {domains};
let cur = -1;
const q = document.getElementById('q'), dom = document.getElementById('dom');
const list = document.getElementById('list'), detail = document.getElementById('detail');

function esc(s) {{ return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}
function show(rows) {{
  list.innerHTML = rows.map(t => `<div class="item" data-i="${{t.i}}">
      <div class="nm">${{esc(t.name)}}</div>
      <div class="meta">${{esc(DOMAINS[t.domain])}} · ${{t.relevance}} · ${{t.transfer}}</div>
      <div class="meta">${{esc(t.desc_cn)}}</div></div>`).join('') || '<div class="empty">没有匹配的工具。</div>';
  document.getElementById('stat').textContent = rows.length + ' / ' + DATA.length + ' 件';
  list.querySelectorAll('.item').forEach(el => el.onclick = () => pick(+el.dataset.i));
}}
function pick(i) {{
  cur = i;
  list.querySelectorAll('.item').forEach(el => el.classList.toggle('on', +el.dataset.i === i));
  const t = DATA.find(x => x.i === i);
  let h = `<h2>${{esc(t.name)}}</h2>
    <div><span class="tag">${{esc(DOMAINS[t.domain])}}</span><span class="tag">相关性 ${{t.relevance}}</span>
    <span class="tag">可迁移 ${{t.transfer}}</span><span class="tag">${{esc(t.module)}}</span></div>
    <p>${{esc(t.desc_cn)}}</p>`;
  if (t.plain) h += `<h3>这个工具做什么</h3><p>${{esc(t.plain)}}</p>`;
  if (t.desc_raw) h += `<h3>源码原话</h3><p>${{esc(t.desc_raw)}}</p>`;
  if (t.params.length) {{
    h += `<h3>输入</h3><table><tr><th>参数</th><th>类型</th><th>必填</th><th>默认</th><th>说明</th></tr>`
      + t.params.map(p => `<tr><td><code>${{esc(p.name)}}</code></td><td>${{esc(p.type||'—')}}</td>
        <td>${{p.required?'是':'否'}}</td><td>${{p.default?('<code>'+esc(p.default)+'</code>'):'—'}}</td>
        <td>${{esc(p.desc||'—')}}</td></tr>`).join('') + `</table>`;
  }}
  if (t.returns.length) {{
    h += `<h3>输出</h3><table><tr><th>字段</th><th>类型</th><th>说明</th></tr>`
      + t.returns.map(r => `<tr><td><code>${{esc(r.name)}}</code></td><td>${{esc(r.type||'—')}}</td>
        <td>${{esc(r.desc||'—')}}</td></tr>`).join('') + `</table>`;
  }}
  h += `<h3>依赖与运行</h3><p>依赖：${{esc(t.dep)}}<br>异常：${{esc(t.guard_text)}}</p>`;
  h += `<h3>调用</h3><pre><code>${{esc(t.py)}}</code></pre><pre><code>${{esc(t.json)}}</code></pre>`;
  if (t.ex) {{
    h += `<h3>示例${{t.ex.status === 'constructed' ? '（构造示意，未实际运行）' : '（实际运行）'}}</h3>`;
    if (t.ex.status === 'constructed') h += `<p class="dim">⚠️ 本机缺少该工具所需的外部服务，返回按源码字段结构手写。</p>`;
    if (t.ex.status === 'demo') h += `<p class="dim">⚠️ 工具确实运行了，但输入与适用场景不完全对应，只说明接口怎么用。</p>`;
    if (t.ex.inputs && t.ex.inputs.length) h += `<p class="dim">数据：${{esc(t.ex.inputs.join('；'))}}</p>`;
    if (t.ex.in) h += `<figure><img src="${{t.ex.in}}" alt="示例输入" onclick="openLB(this)" title="点击放大"><figcaption>示例输入</figcaption></figure>`;
    h += `<pre><code>${{esc(t.ex.out)}}</code></pre>`;
    if (t.ex.img) h += `<figure><img src="${{t.ex.img}}" alt="示例输出" onclick="openLB(this)" title="点击放大"><figcaption>${{esc(t.ex.cap||'示例输出')}}</figcaption></figure>`;
    if (t.ex.note) h += `<p class="dim">${{esc(t.ex.note)}}</p>`;
  }}
  h += `<h3>适用边界</h3><p>${{esc(t.boundary || '未做专项实测，按代码契约推定。')}}</p>`;
  if (t.pitfall) h += `<p><b>坑：</b>${{esc(t.pitfall)}}</p>`;
  if (t.tip) h += `<p><b>建议：</b>${{esc(t.tip)}}</p>`;
  detail.innerHTML = h;
}}
function filter() {{
  const kw = q.value.trim().toLowerCase(), d = dom.value;
  const rows = DATA.filter(t => (!d || t.domain === d) &&
    (!kw || (t.name + ' ' + t.desc_cn + ' ' + t.keywords).toLowerCase().includes(kw)));
  show(rows);
}}
q.oninput = filter; dom.onchange = filter; filter();
</script>
</body>
</html>
"""


# 模板里的 {{ }} 是为可读性写的转义，渲染前还原为单个花括号
HTML_TPL = HTML_TPL.replace("{{", "{").replace("}}", "}")


# 模板里的 {{ }} 是为可读性写的转义，渲染前还原为单个花括号
HTML_TPL = HTML_TPL.replace("{{", "{").replace("}}", "}")


def example_payload(t: dict, folder: str) -> dict | None:
    """索引页用的示例数据；只读 examples/ 下已有的文件，不重复计算。"""
    ex = ROOT / "examples" / folder / t["name"]
    meta_p = ex / "meta.json"
    if not meta_p.exists():
        return None
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    figs = meta.get("figures", {})
    out_key = next((k for k in ("out", "mask") if k in figs), None)
    base = f"../examples/{folder}/{t['name']}"
    out_path = ex / "output.json"
    return {
        "inputs": meta.get("inputs", []),
        "in": f"{base}/in.webp" if figs.get("in") else "",
        "img": f"{base}/{figs[out_key]}" if out_key else "",
        "cap": meta.get("caption", ""),
        "note": meta.get("note", "").replace("`", "").replace("**", ""),
        "status": meta.get("status", "real"),
        "out": out_path.read_text(encoding="utf-8").strip()[:1600] if out_path.exists() else "",
    }


def render_html(tools: list[dict]) -> str:
    folder_of = dict(content.DOMAINS)
    opts = '<option value="">全部域</option>' + "".join(
        f'<option value="{k}">{v}</option>' for k, v in content.DOMAINS)
    data = []
    for i, t in enumerate(tools):
        args = example_args(t)
        kw = ", ".join(f"{k}={py_repr(v)}" for k, v in args.items())
        data.append({
            "i": i, "name": t["name"], "module": t["module"], "domain": t["domain"],
            "relevance": t["relevance"], "transfer": t["transfer"],
            "desc_cn": t["desc_cn"], "desc_raw": t["desc_raw"][:300] if t["desc_raw"] != t["desc_cn"] else "",
            "plain": content.PLAIN.get(t["name"], ""),
            "dep": t["dep"], "guard_text": guard_text(t),
            "params": [{"name": p["name"], "type": short_type(p["type"]), "required": p["required"],
                        "default": p["default"], "desc": p["desc"]} for p in t["params_doc"]],
            "returns": t["returns_doc"],
            "boundary": t["boundary"], "pitfall": t["pitfall"], "tip": t["tip"],
            "keywords": " ".join(p["name"] for p in t["params_doc"]),
            "py": f"from dora.tools.{t['module']} import {t['func']}\nimport json\n"
                  f"res = json.loads({t['func']}({kw}))",
            "json": json.dumps({"name": t["name"], "arguments": args}, ensure_ascii=False, indent=2),
            "ex": example_payload(t, folder_of[t["domain"]]),
        })
    domains = {k: v for k, v in content.DOMAINS}
    return (HTML_TPL.replace("{n_total}", str(len(tools)))
            .replace("{options}", opts)
            .replace("{data}", json.dumps(data, ensure_ascii=False))
            .replace("{domains}", json.dumps(domains, ensure_ascii=False)))


README_TPL = """# DORA 工具库 · 可读版

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
"""


def main() -> int:
    tools = json.loads(TOOLS_JSON.read_text(encoding="utf-8"))
    tools = enrich(tools)
    folder_of = dict(content.DOMAINS)

    folder_by_tool = {t["name"]: folder_of[t["domain"]] for t in tools}

    # 直接覆盖写，不整目录删除：删除 100+ 文件容易误伤，也过不了本地安全钩子
    (DOCS / "99-附录").mkdir(parents=True, exist_ok=True)

    # 逐域
    for key, folder in content.DOMAINS:
        sub = [t for t in tools if t["domain"] == key]
        d = DOCS / folder
        d.mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(render_domain(key, folder, sub), encoding="utf-8", newline="\n")
        for t in sub:
            (d / f"{t['name']}.md").write_text(render_tool(t, folder, folder_by_tool), encoding="utf-8", newline="\n")

    # 顶层与附录
    (DOCS / "00-快速开始.md").write_text(content.QUICKSTART, encoding="utf-8", newline="\n")
    (DOCS / "01-工具全景.md").write_text(content.OVERVIEW_MD, encoding="utf-8", newline="\n")
    for fn, txt in [("A-接入红线.md", content.APPENDIX_A), ("B-已知陷阱.md", content.APPENDIX_B),
                    ("C-评测结论摘要.md", content.APPENDIX_C), ("D-术语.md", content.APPENDIX_D)]:
        (DOCS / "99-附录" / fn).write_text(txt, encoding="utf-8", newline="\n")

    # 索引
    (INDEX / "INDEX.md").write_text(render_index_md(tools), encoding="utf-8", newline="\n")
    (INDEX / "index.html").write_text(render_html(tools), encoding="utf-8", newline="\n")
    (INDEX / "tools.json").write_text(json.dumps(tools, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    (ROOT / "README.md").write_text(README_TPL, encoding="utf-8", newline="\n")

    n = len(list(DOCS.rglob("*.md")))
    print(f"工具页：{len(tools)} 件；docs 下 md 共 {n} 个；index 已生成 index.html / INDEX.md / tools.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
