#!/usr/bin/env python
"""Static validation for the math-modeling-paper skill.

Checks structure, internal links, and a small set of retained/removed invariants.
It does NOT execute the workflow and cannot prove behavioural correctness.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SKILL_NAME = "math-modeling-paper"

# Only explicit example regions in the two designated documents are exempt.
# No disclaimer or file name exempts the rest of a file from scanning.
FORBIDDEN = [
    ("国一 ≥10 张", "图表数量配额"),
    ("国一≥10", "图表数量配额"),
    ("省一→国二的分水岭", "奖级映射"),
    ("纯仿真=二等奖上限", "奖级映射"),
    ("60% 严于", "查重口径混淆"),
    ("严于全国 25%", "查重口径混淆"),
    ("赛区要求高于全国", "层级倒置"),
    ("山西赛区要点 > 官方", "层级倒置"),
    ("单人队无此风险", "教师禁令误判"),
    ("赛规 <40%", "虚构 AIGC 阈值"),
    ("格式 13 条", "格式条数错误"),
    ("DE 精度 > PSO", "算法排名"),
    ("唯一可靠方案", "绝对化"),
    ("任何常微分方程数值解", "刚性/非刚性混淆"),
]

# Phrases that must remain available somewhere in the skill.
RETAINED = [
    ("封版", "封版/副本权限门"),
    ("AI 工具使用详情", "AI 披露四要件"),
    ("本地成功不等于平台收件", "平台收件边界"),
    ("独立", "独立复核/独立完成"),
]

LINK_RE = re.compile(r"`((?:references|templates|scripts)/[^`\s]+?\.(?:md|py))`")


def load_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    data = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith((" ", "\t", "#")):
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip().strip('"')
    return data


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    skill_md = root / "SKILL.md"
    problems: list[str] = []
    checks = 0

    if not skill_md.exists():
        print(json.dumps({"ok": False, "error": "SKILL.md missing"}, ensure_ascii=False))
        return 1

    text = skill_md.read_text(encoding="utf-8")
    fm = load_frontmatter(text)

    # 1. Frontmatter
    checks += 1
    if fm.get("name") != SKILL_NAME:
        problems.append(f"frontmatter name != {SKILL_NAME}: {fm.get('name')!r}")
    checks += 1
    desc = fm.get("description", "")
    if not desc or len(desc) > 200:
        problems.append(f"description missing or too long ({len(desc)} chars)")
    checks += 1
    version = fm.get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        problems.append(f"version not semver: {version!r}")

    # 2. Resolve internal links in every Markdown document, not only the index.
    all_docs = {p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
                for p in sorted(root.rglob("*.md"))}
    links = sorted({rel for body in all_docs.values() for rel in LINK_RE.findall(body)})
    for rel in links:
        checks += 1
        target = (root / rel).resolve()
        if not target.is_relative_to(root.resolve()):
            problems.append(f"internal link escapes skill root: {rel}")
        elif not target.is_file():
            problems.append(f"broken link: {rel}")

    # 3. Markdown code fences must close; longer fences may contain shorter ones.
    for rel, body in all_docs.items():
        checks += 1
        opened = None
        for lineno, line in enumerate(body.splitlines(), 1):
            match = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
            if match:
                mark, suffix = match.groups()
                if opened is None:
                    opened = (mark[0], len(mark), lineno)
                elif mark[0] == opened[0] and len(mark) >= opened[1] and not suffix.strip():
                    opened = None
        if opened is not None:
            problems.append(f"unclosed code fence: {rel}:{opened[2]}")

    # 3. Orphan check: every reference/template file mentioned by name should be linked from SKILL.md
    for sub in ("references", "templates", "scripts"):
        d = root / sub
        if not d.exists():
            continue
        for p in sorted(d.iterdir()):
            if not p.is_file():
                continue
            rel = f"{sub}/{p.name}"
            checks += 1
            if rel not in text:
                problems.append(f"not referenced from SKILL.md: {rel}")

    # 4. Only explicitly marked examples in two documentation files are exempt.
    # The rest of each file remains active; a disclaimer cannot whitelist a file.
    META_FILES = {"references/maintenance-decisions.md", "templates/behavior-probes.md"}
    all_text = dict(all_docs)
    scan_text = {}
    for rel, body in all_text.items():
        if "<!-- examples:" in body:
            checks += 1
            if rel not in META_FILES:
                problems.append(f"example exemption not allowed in: {rel}")
            if body.count("<!-- examples:start -->") != body.count("<!-- examples:end -->"):
                problems.append(f"unbalanced example region: {rel}")
        scan_text[rel] = (re.sub(r"<!-- examples:start -->.*?<!-- examples:end -->", "", body, flags=re.S)
                          if rel in META_FILES else body)
    for phrase, label in FORBIDDEN:
        checks += 1
        hits = [rel for rel, body in scan_text.items() if phrase in body]
        if hits:
            problems.append(f"forbidden phrase {phrase!r} ({label}) in: {', '.join(hits)}")

    # 5. Retained invariants present somewhere
    corpus = "\n".join(all_text.values())
    for phrase, label in RETAINED:
        checks += 1
        if phrase not in corpus:
            problems.append(f"missing retained concept: {label} ({phrase!r})")

    # 6. No leftover placeholders
    checks += 1
    for bad in ("TODO", "FIXME", "PLACEHOLDER"):
        if bad in text:
            problems.append(f"placeholder token in SKILL.md: {bad}")

    # Parse bundled Python without importing or executing any of it.
    for source in sorted(root.rglob("*.py")):
        checks += 1
        try:
            compile(source.read_text(encoding="utf-8"), str(source), "exec")
        except (SyntaxError, UnicodeError) as error:
            problems.append(f"invalid Python: {source.relative_to(root).as_posix()}: {error}")

    # 7. Files count
    counts = {sub: len(list((root / sub).iterdir())) if (root / sub).exists() else 0
              for sub in ("references", "templates", "scripts")}

    result = {
        "skill": str(root),
        "version": version,
        "checks": checks,
        "problems": problems,
        "ok": not problems,
        "files": counts,
        "links": len(links),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not problems else 2


if __name__ == "__main__":
    sys.exit(main())
