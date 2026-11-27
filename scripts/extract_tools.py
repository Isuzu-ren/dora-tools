#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从源码提取 108 件工具的结构化信息，与既有评估表合并，输出 index/tools.json。

不做任何修改：只读 src/dora/tools/*.py 与主仓库的工具清单附录。

    python scripts/extract_tools.py
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "dora" / "tools"
APPENDIX = Path("D:/research/DORA/my/DORA_工具清单与水旱项目相关性评估.md")
OUT = ROOT / "index" / "tools.json"

MODULES = ["perception", "analysis", "calculate", "vis", "poi", "model", "terrain"]

# 本仓库在上游 108 件之外新增的工具：上游清单里没有它们，标签在此手工给出。
# origin=extension 会写进 tools.json，文档据此加「本地扩展」标注。
EXTENSION_MODULES = {"terrain"}
EXTRA_META = {
    "ras.terrain": {"relevance": "★★★", "transfer": "A",
                    "usage": "一次出坡度/坡向/曲率/TRI/TPI/粗糙度，地形地貌分析的地基",
                    "dep": "numpy"},
    "ras.flow": {"relevance": "★★★", "transfer": "A",
                 "usage": "填洼→流向→汇流，流域提取与洪水演进的前置",
                 "dep": "numpy"},
    "ras.contour": {"relevance": "★★", "transfer": "A",
                    "usage": "等高线出图、坡度分级底图",
                    "dep": "skimage"},
    "ras.catchment": {"relevance": "★★★", "transfer": "A",
                      "usage": "给定出水口反查上游汇水区，洪水预报的单元划分",
                      "dep": "numpy / shapely"},
    "ras.geomorphons": {"relevance": "★★★", "transfer": "A",
                        "usage": "10 类地貌单元分类，地貌分区与易发性解释变量",
                        "dep": "numpy"},
    "ras.river_network": {"relevance": "★★★", "transfer": "A",
                          "usage": "河网矢量化为河段并做 Strahler 分级，洪水演进与水质的基本单元",
                          "dep": "numpy / shapely"},
}

# 功能域（主域唯一）。键为 MCP 工具名，值为域名 key。
DOMAINS = [
    ("water", "10-水体与淹没"),
    ("asset", "20-承灾体"),
    ("terrain", "30-地形与地表变化"),
    ("raster", "40-栅格分析"),
    ("vector", "50-矢量与空间关系"),
    ("compute", "60-计算与决策"),
    ("carto", "70-制图与报告"),
    ("poi", "80-POI-点位"),
    ("other", "90-其他感知"),
]

DOMAIN_OF: dict[str, str] = {}


def assign(domain: str, *names: str) -> None:
    for n in names:
        DOMAIN_OF[n] = domain


# —— 感知类：按对象分 ——
assign("water", "seg.flood", "seg.water_aerial", "seg.reservoir")
assign("asset",
       "seg.building_damage", "seg.building_damage_opt_sar", "seg.road_damage",
       "seg.bridge", "seg.storage_tank", "seg.harbor", "seg.reconstruction_building",
       "seg.building_lowres", "seg.vehicle_trapped_aerial", "seg.road_debris_aerial",
       "seg.building_intact_aerial", "seg.building_damage_aerial",
       "seg.building_destroyed_aerial", "seg.road_intact_aerial")
assign("terrain", "seg.landslide_ms", "seg.landslide_bitemporal", "seg.vegetation",
       "ras.slope", "ras.hillshade", "ras.terrain", "ras.flow", "ras.contour",
       "ras.catchment", "ras.geomorphons", "ras.river_network")
assign("other",
       "seg.lava", "seg.plane", "seg.ship", "seg.vehicle", "seg.pool_aerial",
       "seg.swimming_pool", "seg.playground", "seg.roundabout",
       "seg.tree_fallen_aerial", "seg.tree_standing_aerial", "seg.vehicle_free_aerial")

# —— 其余按前缀兜底 ——
DEFAULT_BY_PREFIX = {"ras.": "raster", "mask.": "raster", "vec.": "vector",
                     "calc.": "compute", "logi.": "compute", "tool.": "compute",
                     "vis.": "carto", "poi.": "poi", "report.": "carto",
                     "model.": "carto"}


def classify(name: str) -> str:
    if name in DOMAIN_OF:
        return DOMAIN_OF[name]
    for p, d in DEFAULT_BY_PREFIX.items():
        if name.startswith(p):
            return d
    return "other"


def parse_module(path: Path) -> list[dict]:
    """抽 @mcp.tool 装饰的函数：名称、签名、docstring、装饰器、行号。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    src = path.read_text(encoding="utf-8").splitlines()
    tools = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        mcp_name, has_guard, desc = None, False, ""
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call):
                f = dec.func
                fname = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
                if fname == "tool":
                    for kw in dec.keywords:
                        if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                            mcp_name = kw.value.value
                        elif kw.arg == "description" and isinstance(kw.value, ast.Constant):
                            desc = kw.value.value
                elif fname == "_tool_guard":
                    has_guard = True
        if not mcp_name:
            continue

        args = node.args
        defaults = [None] * (len(args.args) - len(args.defaults)) + list(args.defaults)
        params = []
        for a, d in zip(args.args, defaults):
            params.append({
                "name": a.arg,
                "type": ast.unparse(a.annotation) if a.annotation else None,
                "required": d is None,
                "default": None if d is None else ast.unparse(d),
            })
        doc = (desc or "").strip() or (ast.get_docstring(node) or "").strip()
        ART = {"mask_path", "output_path", "vector_path", "table_path", "graph_path",
               "clip_path", "links_geojson", "intersection_path", "route_path"}
        artifacts = sorted({n.value for n in ast.walk(node)
                            if isinstance(n, ast.Constant) and isinstance(n.value, str)
                            and n.value in ART})
        end = (node.end_lineno or node.lineno)
        tools.append({
            "name": mcp_name,
            "func": node.name,
            "module": path.stem,
            "source": f"src/dora/tools/{path.name}",
            "lineno": node.lineno,
            "loc": end - node.lineno + 1,
            "signature": ast.unparse(node.args),
            "params": params,
            "docstring": doc,
            "artifacts": artifacts,
            "guarded": has_guard,
            "body_lines": src[node.lineno - 1:end],
        })
    return tools


def parse_appendix() -> dict[str, dict]:
    """从主仓库附录 A 取「相关性 / 可迁移性 / 用法」。"""
    if not APPENDIX.exists():
        return {}
    out = {}
    for line in APPENDIX.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 7:
            continue
        name = cells[0].strip("`")
        out[name] = {"relevance": cells[4], "transfer": cells[5], "usage": cells[6],
                     "dep": cells[3]}
    return out


def main() -> int:
    tools = []
    for m in MODULES:
        tools.extend(parse_module(SRC / f"{m}.py"))

    app = parse_appendix()
    for t in tools:
        meta = app.get(t["name"], {})
        t["origin"] = "extension" if t["module"] in EXTENSION_MODULES else "upstream"
        if t["origin"] == "extension":
            meta = {**EXTRA_META.get(t["name"], {}), **meta}
        t["relevance"] = meta.get("relevance")
        t["transfer"] = meta.get("transfer")
        t["usage"] = meta.get("usage")
        t["dep"] = meta.get("dep")
        t["domain"] = classify(t["name"])
        # 正文里是否出现 try/except（决定「报错行为」怎么写）
        t["has_try"] = any("try:" in ln for ln in t["body_lines"])
        del t["body_lines"]

    tools.sort(key=lambda t: (t["domain"], t["name"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(tools, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- 核对 ----
    print(f"工具总数：{len(tools)}")
    by_mod = {}
    for t in tools:
        by_mod[t["module"]] = by_mod.get(t["module"], 0) + 1
    print("按模块：", by_mod)

    by_dom = {}
    for t in tools:
        by_dom[t["domain"]] = by_dom.get(t["domain"], 0) + 1
    print("\n按功能域：")
    for key, folder in DOMAINS:
        names = [t["name"] for t in tools if t["domain"] == key]
        print(f"  {folder:<18} {by_dom.get(key,0):>3}   {', '.join(names[:4])}{' …' if len(names) > 4 else ''}")

    miss_app = [t["name"] for t in tools if not t["relevance"]]
    print(f"\n附录未匹配：{miss_app or '无'}")
    no_doc = [t["name"] for t in tools if not t["docstring"]]
    print(f"无 docstring：{no_doc or '无'}")
    print(f"带 _tool_guard：{sum(1 for t in tools if t['guarded'])} / {len(tools)}")
    print(f"写完 {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
