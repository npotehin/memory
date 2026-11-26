#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────
#  ПРОИСХОЖДЕНИЕ: НАШЕ, НАПИСАНО С НУЛЯ
#  Автор: ИИ-Консьерж для Никиты Потехина, 25-26.11.2026
# ─────────────────────────────────────────────────────────────────────────
# -*- coding: utf-8 -*-
"""Собирает styles/index.html — галерею стилей из папки styles/."""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
STYLES = ROOT / "styles"

CSS = """
:root{--bg:#f4f2ee;--card:#fff;--ink:#1d1d1f;--mut:#6b665f;--line:#e2ded7;--soft:#faf8f5}
@media(prefers-color-scheme:dark){:root{--bg:#0f0f10;--card:#1c1c1e;--ink:#f2f2f7;--mut:#98989f;--line:#333;--soft:#242426}}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Arial,sans-serif;
background:var(--bg);color:var(--ink);font-size:16px;line-height:1.6;padding:0 12px 60px}
.wrap{max-width:820px;margin:0 auto}
h1{font-size:26px;letter-spacing:-.02em;margin:26px 0 4px}
.sub{color:var(--mut);font-size:14px;margin:0 0 22px}
.card{display:block;text-decoration:none;color:inherit;background:var(--card);border:1px solid var(--line);
border-radius:14px;padding:16px 18px;margin:11px 0}
.card:active{transform:scale(.995)}
.card b{display:block;font-size:16px;margin-bottom:2px}
.card span{color:var(--mut);font-size:13.5px}
.foot{margin-top:28px;padding-top:16px;border-top:1px solid var(--line);color:var(--mut);font-size:12.5px}
"""

def main():
    items = []
    if STYLES.exists():
        for f in sorted(STYLES.glob("*.html")):
            if f.name == "index.html":
                continue
            items.append(f)
    cards = []
    for f in items:
        cards.append(
            '<a class="card" href="%s"><b>%s</b><span>%s</span></a>'
            % (f.name, f.stem.replace("-", " "), "стиль оформления")
        )
    if not cards:
        cards.append('<p class="sub">Пока нет файлов в папке styles/.</p>')

    doc = ("<!DOCTYPE html><html lang=\"ru\"><head><meta charset=\"utf-8\">"
           "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
           "<title>Стили</title><style>%s</style></head><body><div class=\"wrap\">"
           "<h1>Стили отчётов</h1>"
           "<p class=\"sub\">Выберите и посмотрите на телефоне.</p>%s"
           "<div class=\"foot\">ИИ-Консьерж · memory</div></div></body></html>"
           % (CSS, "".join(cards)))

    out = STYLES / "index.html"
    out.write_text(doc, encoding="utf-8")
    print("OK", out, len(doc), "bytes")

if __name__ == "__main__":
    main()
