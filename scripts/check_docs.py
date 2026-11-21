#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""文档自检：件数、参数一致性、死链、索引完整性。

    python scripts/check_docs.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX = ROOT / "index"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import content  # noqa: E402

errors: list[str] = []
warns: list[str] = []


def main() -> int:
    tools = json.loads((INDEX / "tools.json").read_text(encoding="utf-8"))
    folder_of = dict(content.DOMAINS)

    # 1. 件数与域分布
    if len(tools) != 108:
        errors.append(f"tools.json 应有 108 件，实为 {len(tools)}")
    per_dom = {}
    for t in tools:
        per_dom[t["domain"]] = per_dom.get(t["domain"], 0) + 1
    if sum(per_dom.values()) != 108:
        errors.append(f"域名分布合计 {sum(per_dom.values())}，应为 108")
    for key, _ in content.DOMAINS:
        if key not in per_dom:
            errors.append(f"域 {key} 没有工具")

    # 2. 每件工具页存在，且参数名与签名一致
    pages = 0
    for t in tools:
        page = DOCS / folder_of[t["domain"]] / f"{t['name']}.md"
        if not page.exists():
            errors.append(f"缺页面 {page.relative_to(ROOT)}")
            continue
        pages += 1
        text = page.read_text(encoding="utf-8")
        missing = [p["name"] for p in t["params"] if f"`{p['name']}`" not in text]
        if missing:
            errors.append(f"{t['name']} 页面缺参数行：{missing}")
        if t["name"] not in text.splitlines()[0]:
            errors.append(f"{t['name']} 页面标题不对")

    # 3. 死链（相对链接 .md）
    n_links = 0
    for md in DOCS.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)#]+\.md)\)", text):
            n_links += 1
            target = (md.parent / link).resolve()
            if not target.exists():
                errors.append(f"死链 {md.relative_to(ROOT)} → {link}")

    # 4. 索引完整性
    idx = (INDEX / "INDEX.md").read_text(encoding="utf-8")
    for t in tools:
        if f"`{t['name']}`" not in idx:
            errors.append(f"INDEX.md 缺 {t['name']}")
    html = (INDEX / "index.html").read_text(encoding="utf-8")
    for t in tools:
        if f'"name": "{t["name"]}"' not in html:
            errors.append(f"index.html 缺 {t['name']}")
            break

    # 5. 相关性 / 可迁移性齐全
    for t in tools:
        if not t.get("relevance") or not t.get("transfer"):
            warns.append(f"{t['name']} 缺相关性或可迁移性标签")

    # 6. 未写「适用边界」补充说明的工具（不算错，提示）
    no_note = [t["name"] for t in tools if not t.get("boundary") and not t.get("pitfall") and not t.get("tip")]
    if no_note:
        warns.append(f"{len(no_note)} 件仅有通用边界说明：{', '.join(no_note[:6])} …")

    print(f"工具页 {pages}/108；相对链接 {n_links} 条；域 {len(per_dom)} 个")
    print(f"警告 {len(warns)} 条")
    for w in warns[:5]:
        print("  ! " + w)
    if errors:
        print(f"\n错误 {len(errors)} 条：")
        for e in errors[:20]:
            print("  × " + e)
        return 1
    print("\n自检通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
