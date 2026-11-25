#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает index.html — ленту изменений: все HTML-файлы репозитория с датами."""

import pathlib
import json
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent

CSS = """
:root{--bg:#f4f2ee;--card:#fff;--ink:#1d1d1f;--mut:#6b665f;--line:#e2ded7;--soft:#faf8f5;--acc:#2b7a4b}
@media(prefers-color-scheme:dark){:root{--bg:#0f0f10;--card:#1c1c1e;--ink:#f2f2f7;--mut:#98989f;--line:#333;--soft:#242426;--acc:#4aa06a}}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Arial,sans-serif;
background:var(--bg);color:var(--ink);font-size:16px;line-height:1.6;padding:0 12px 60px}
.wrap{max-width:820px;margin:0 auto}
.hero{padding:22px 0 6px}
.k{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--mut);font-weight:600}
h1{font-size:27px;letter-spacing:-.02em;margin:8px 0 6px;line-height:1.2}
.sub{color:var(--mut);font-size:14px;margin:0 0 20px}
.sect{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--mut);
font-weight:700;margin:26px 0 8px}
.row{display:flex;gap:11px;align-items:flex-start;background:var(--card);border:1px solid var(--line);
border-radius:13px;padding:13px 15px;margin:9px 0;text-decoration:none;color:inherit}
.row:active{transform:scale(.995)}
.ic{flex:0 0 32px;height:32px;border-radius:9px;background:var(--soft);border:1px solid var(--line);
display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:var(--mut)}
.body{flex:1;min-width:0}
.body b{display:block;font-size:15px;margin-bottom:1px}
.body span{color:var(--mut);font-size:13px}
.date{flex:0 0 auto;color:var(--mut);font-size:12px;font-variant-numeric:tabular-nums;padding-top:3px}
.foot{margin-top:30px;padding-top:16px;border-top:1px solid var(--line);color:var(--mut);font-size:12.5px}
"""


def git_dates():
    """path -> последняя дата коммита (или mtime)."""
    dates = {}
    try:
        out = subprocess.check_output(
            ["git", "log", "--name-only", "--pretty=format:%cd", "--date=short"],
            cwd=str(ROOT), text=True, stderr=subprocess.DEVNULL)
        cur = None
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            if len(line) == 10 and line[4] == "-" and line[7] == "-":
                cur = line
            else:
                if cur and line not in dates:
                    dates[line] = cur
    except Exception:
        pass
    return dates


def collect():
    files = []
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT).as_posix()
        if rel == "index.html" or rel.endswith("styles/index.html"):
            continue
        files.append(p)
    return files


def human(path, dates):
    rel = path.relative_to(ROOT).as_posix()
    d = dates.get(rel)
    if not d:
        import datetime
        d = datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()
    title = path.stem.replace("-", " ").replace("_", " ")
    return rel, title, d


def main():
    dates = git_dates()
    files = collect()
    rows = sorted((human(p, dates) for p in files), key=lambda t: t[2], reverse=True)

    groups = {}
    for rel, title, d in rows:
        if rel.startswith("styles/"):
            g = "Стили"
        elif rel.startswith("projects/"):
            g = "Проекты"
        else:
            g = "Отчёты"
        groups.setdefault(g, []).append((rel, title, d))

    html_parts = []
    html_parts.append('<a class="row" href="skills.html"><div class="ic">SK</div>'
                      '<div class="body"><b>Скиллы</b><span>что установлено, из чего состоит</span></div>'
                      '<div class="date">каталог</div></a>')
    for g in ("Отчёты", "Стили", "Проекты"):
        if g not in groups:
            continue
        html_parts.append('<div class="sect">%s</div>' % g)
        for rel, title, d in groups[g]:
            icon = "ST" if g == "Стили" else ("PR" if g == "Проекты" else "RE")
            html_parts.append(
                '<a class="row" href="%s"><div class="ic">%s</div>'
                '<div class="body"><b>%s</b><span>%s</span></div>'
                '<div class="date">%s</div></a>'
                % (rel, icon, title, rel, d[8:10] + "." + d[5:7] if len(d) == 10 else d)
            )

    doc = ("<!DOCTYPE html><html lang=\"ru\"><head><meta charset=\"utf-8\">"
           "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
           "<meta name=\"theme-color\" content=\"#f4f2ee\">"
           "<title>Память — обновления</title><style>%s</style></head><body><div class=\"wrap\">"
           "<div class=\"hero\"><div class=\"k\">ИИ-Консьерж</div>"
           "<h1>Обновления</h1>"
           "<p class=\"sub\">Всё, что собрано: отчёты, стили, проекты. Обновите страницу — увидите новое.</p></div>"
           "%s<div class=\"foot\">memory · Npotehinru</div></div></body></html>"
           % (CSS, "".join(html_parts)))

    out = ROOT / "index.html"
    out.write_text(doc, encoding="utf-8")
    print("OK", len(rows), "files ->", out)


if __name__ == "__main__":
    main()
