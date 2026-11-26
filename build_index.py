#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────
#  ПРОИСХОЖДЕНИЕ: НАШЕ, НАПИСАНО С НУЛЯ
#  Автор: ИИ-Консьерж для Никиты Потехина, 25-26.11.2026
# ─────────────────────────────────────────────────────────────────────────
# -*- coding: utf-8 -*-
"""Собирает index.html — ленту по группам: все HTML-страницы репозитория.

Правила:
  * шаблоны скилла (templates/, origin/) в ленту не попадают;
  * группы задаются явно, неизвестное уходит в «Отчёты»;
  * у ссылки проверяется, что файл существует, иначе строки нет;
  * ORIGIN.md показывается как страница, а не как файл на скачивание.
"""

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
.sub{color:var(--mut);font-size:14px;margin:0 0 8px}
.nav{position:sticky;top:0;z-index:5;background:var(--bg);display:flex;gap:7px;overflow-x:auto;
padding:10px 12px;margin:0 -12px 4px;border-bottom:1px solid var(--line);scrollbar-width:none}
.nav::-webkit-scrollbar{display:none}
.nav a{flex:0 0 auto;font-size:12.5px;padding:6px 11px;border-radius:999px;border:1px solid var(--line);
background:var(--card);color:var(--mut);text-decoration:none;font-weight:600}
.nav a:active{background:var(--soft)}
.sect{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--mut);
font-weight:700;margin:26px 0 8px;scroll-margin-top:62px}
.row{display:flex;gap:11px;align-items:flex-start;background:var(--card);border:1px solid var(--line);
border-radius:13px;padding:13px 15px;margin:9px 0;text-decoration:none;color:inherit}
.row:active{transform:scale(.995)}
.ic{flex:0 0 32px;height:32px;border-radius:9px;background:var(--soft);border:1px solid var(--line);
display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:var(--mut)}
.body{flex:1;min-width:0}
.body b{display:block;font-size:15px;margin-bottom:1px}
.body span{color:var(--mut);font-size:12.5px}
.date{flex:0 0 auto;color:var(--mut);font-size:12px;font-variant-numeric:tabular-nums;padding-top:3px}
.foot{margin-top:30px;padding-top:16px;border-top:1px solid var(--line);color:var(--mut);font-size:12.5px}
.foot a{color:inherit}
"""

# ─── Группы ───────────────────────────────────────────────────────────────
# (ключ, заголовок, иконка, предикат по пути, подпись строки)
GROUPS = [
    ("assistant", "Ассистент", "AI", lambda r: r in (
        "assistant-map.html", "assistant-bounds.html", "ORIGIN.md"),
     "устройство, границы, авторство"),
    ("catalog", "Каталог", "SK", lambda r: r in (
        "skills.html", "skills-export-report.html",
        "skills-origin-audit.html", "skills-origin-audit.md"),
     "скиллы и что установлено"),
    ("skill-cards", "Карточки скиллов", "SC", lambda r: r.startswith("skills/") and r != "skills/index.html",
     "разбор одного скилла"),
    ("reports", "Отчёты", "RE", lambda r: not any(p(r) for _, _, _, p, _ in GROUPS[:-1])
     and not r.startswith("styles/") and not r.startswith("projects/")
     and not r.startswith("skills-src/") and not r.startswith("guide/"),
     ""),
    ("guides", "Инструкции", "IN", lambda r: r in (
        "github-cloudflare-guide.html", "setup-guide.html", "cloudflare-setup.html",
        "access-options.html", "login-steps.html", "memory-github.html"),
     "настройка, вход, доступ"),
    ("styles", "Стили", "ST", lambda r: r.startswith("styles/") and not r.endswith("styles/index.html"),
     "оформление отчётов"),
    ("projects", "Проекты", "PR", lambda r: r.startswith("projects/"),
     "описание проекта"),
]

TITLES = {
    "assistant-map.html": ("Карта ассистента", "AI"),
    "assistant-bounds.html": ("Границы ассистента", "AI"),
    "ORIGIN.md": ("Чьё это", "OR"),
    "skills.html": ("Скиллы", "SK"),
    "skills-export-report.html": ("Выгрузка скиллов", "SK"),
    "skills-origin-audit.html": ("Аудит: чьи это скиллы", "SK"),
    "skills-origin-audit.md": ("Аудит скиллов — отчёт (MD)", "SK"),
    "my-code.html": ("Мой код", "RE"),
    "github-cloudflare-guide.html": ("GitHub → Cloudflare", "IN"),
    "setup-guide.html": ("Настройка связки", "IN"),
    "cloudflare-setup.html": ("Cloudflare", "IN"),
    "access-options.html": ("Варианты доступа", "IN"),
    "login-steps.html": ("Шаги входа", "IN"),
    "memory-github.html": ("Память в GitHub", "RE"),
    "styles/01-cards.html": ("Карточки", "ST"),
    "styles/02-spoilers.html": ("Спойлеры", "ST"),
}


def git_dates():
    """path -> последняя дата коммита."""
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


def skip(rel):
    """То, что страницей ленты не является."""
    if rel == "index.html":
        return True
    if rel.startswith("skills-src/"):
        return True          # шаблоны, origin/, SKILL.md
    if rel.startswith("styles/") and rel.endswith("styles/index.html"):
        return True
    if "/origin/" in "/" + rel + "/":
        return True
    if "/templates/" in "/" + rel + "/":
        return True
    return False


def collect():
    files = []
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT).as_posix()
        if skip(rel):
            continue
        if not p.is_file():
            continue
        files.append(p)
    for rel in TITLES:
        p = ROOT / rel
        if p.is_file() and p.suffix == ".md":
            files.append(p)
    return files


def origin_of(rel):
    if rel.startswith("skills-src/") and "/origin/" in "/" + rel + "/":
        return "оригинал"
    if rel.startswith("skills-src/"):
        return "оригинал+правки" if "/scripts/" in rel else "оригинал"
    return "наше"


def title_of(rel):
    if rel in TITLES:
        return TITLES[rel][0], TITLES[rel][1]
    if rel.startswith("skills/"):
        stem = pathlib.Path(rel).stem
        return stem.replace("-", " "), "SC"
    if rel.startswith("projects/"):
        parts = rel.split("/")
        name = parts[-2] if len(parts) > 1 else parts[0]
        return name.upper() if len(name) <= 4 else name, "PR"
    stem = pathlib.Path(rel).stem
    return stem.replace("-", " ").replace("_", " "), "RE"


def human(path, dates):
    rel = path.relative_to(ROOT).as_posix()
    d = dates.get(rel)
    if not d:
        import datetime
        d = datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()
    title, icon = title_of(rel)
    return rel, title, d, origin_of(rel), icon


def check_links(doc):
    """Внутренние ссылки документа — только на существующие файлы."""
    import re
    out = []
    for m in re.finditer(r'href="([^"]+)"', doc):
        h = m.group(1)
        if h.startswith(("#", "http://", "https://", "mailto:")):
            continue
        target = (ROOT / h.split("#")[0])
        if not target.exists():
            out.append(h)
    return out


def main():
    dates = git_dates()
    files = collect()
    rows = sorted((human(p, dates) for p in files), key=lambda t: t[2], reverse=True)

    assigned = {}
    for key, title, icon, pred, sub in GROUPS:
        assigned[key] = []
    for rel, title, d, org, icon in rows:
        placed = False
        for key, _, _, pred, _ in GROUPS:
            if key == "reports":
                continue
            if pred(rel):
                assigned[key].append((rel, title, d, org, icon))
                placed = True
                break
        if not placed:
            assigned["reports"].append((rel, title, d, org, icon))

    # навигация по непустым группам
    nav = []
    order = ["assistant", "catalog", "skill-cards", "guides", "reports", "styles", "projects"]
    meta = {k: (t, i, s) for k, t, i, _, s in GROUPS}
    for key in order:
        if assigned.get(key):
            nav.append('<a href="#%s">%s</a>' % (key, meta[key][0]))

    parts = []
    for key in order:
        items = assigned.get(key) or []
        if not items:
            continue
        title, icon, sub = meta[key]
        head = title if not sub else "%s <span style=\"font-weight:400;text-transform:none;" \
                                         "letter-spacing:0\">· %s</span>" % (title, sub)
        parts.append('<div class="sect" id="%s">%s</div>' % (key, head))
        if key == "styles" and (ROOT / "styles/index.html").exists():
            parts.append(
                '<a class="row" href="styles/index.html"><div class="ic">ST</div>'
                '<div class="body"><b>Галерея стилей</b>'
                '<span>все варианты оформления рядом</span></div>'
                '<div class="date">обзор</div></a>')
        for rel, name, d, org, ic in items:
            tag = {"наше": "наше", "оригинал+правки": "разработчик + наши правки",
                   "оригинал": "разработчик"}[org]
            dd = d[8:10] + "." + d[5:7] if len(d) == 10 else d
            parts.append(
                '<a class="row" href="%s"><div class="ic">%s</div>'
                '<div class="body"><b>%s</b><span>%s</span></div>'
                '<div class="date">%s</div></a>'
                % (rel, ic, name, tag, dd))

    doc = ("<!DOCTYPE html><html lang=\"ru\"><head><meta charset=\"utf-8\">"
           "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
           "<meta name=\"theme-color\" content=\"#f4f2ee\">"
           "<title>Память — обновления</title><style>%s</style></head><body><div class=\"wrap\">"
           "<div class=\"hero\"><div class=\"k\">ИИ-Консьерж</div>"
           "<h1>Память</h1>"
           "<p class=\"sub\">Всё собранное, по разделам. Обновите страницу — увидите новое.</p></div>"
           "<div class=\"nav\">%s</div>"
           "%s<div class=\"foot\">memory · Npotehinru · "
           "<a href=\"ORIGIN.md\">чьё это</a></div></div></body></html>"
           % (CSS, "".join(nav), "".join(parts)))

    # проверка ссылок ленты перед записью
    broken = check_links(doc)
    for b in broken:
        print("БИТАЯ ССЫЛКА:", b)

    out = ROOT / "index.html"
    out.write_text(doc, encoding="utf-8")
    total = sum(len(v) for v in assigned.values())
    print("OK", total, "files ->", out, "| групп:", len(nav), "| битых:", len(broken))


if __name__ == "__main__":
    main()
