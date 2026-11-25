#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка HTML-отчёта из markdown с читаемой вёрсткой."""

import re
import html
import sys

SRC = "/workspace/home/Inbox/becd349dfe277f7a/memory-github.md"
DST = "/workspace/home/Documents/memory-github.html"

CSS = """
* { box-sizing: border-box; }
body {
  margin: 0; padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  background: #f4f2ee; color: #1d1d1f;
  line-height: 1.65; font-size: 17px;
  -webkit-text-size-adjust: 100%;
}
.wrap { max-width: 820px; margin: 0 auto; padding: 24px 18px 80px; }
.hero {
  background: #1d1d1f; color: #fff;
  padding: 40px 26px 34px; border-radius: 18px; margin-bottom: 30px;
}
.hero .kicker {
  font-size: 12px; letter-spacing: .16em; text-transform: uppercase;
  color: #a8a29a; margin-bottom: 14px;
}
.hero h1 { margin: 0 0 12px; font-size: 34px; line-height: 1.2; font-weight: 650; }
.hero p { margin: 0; color: #c9c5be; font-size: 16px; }
.hero .meta {
  margin-top: 22px; padding-top: 18px; border-top: 1px solid #3a3a3c;
  font-size: 13px; color: #8e8a83; display: flex; gap: 22px; flex-wrap: wrap;
}
h2 {
  font-size: 25px; margin: 48px 0 6px; font-weight: 650; letter-spacing: -.01em;
  display: flex; align-items: baseline; gap: 12px;
}
h2 .num {
  font-size: 13px; font-weight: 600; color: #fff; background: #1d1d1f;
  width: 26px; height: 26px; border-radius: 8px; flex: 0 0 26px;
  display: inline-flex; align-items: center; justify-content: center;
  transform: translateY(-3px);
}
h2 + p, h2 + .body { margin-top: 14px; }
h3 { font-size: 18px; margin: 26px 0 8px; font-weight: 650; color: #1d1d1f; }
p { margin: 10px 0; }
.section { margin-bottom: 8px; }

blockquote {
  margin: 16px 0; padding: 16px 20px; background: #fff8e6;
  border-left: 4px solid #d9a41a; border-radius: 0 10px 10px 0;
  color: #4a3d18; font-size: 16px;
}
blockquote p { margin: 0; }

.callout {
  margin: 20px 0; padding: 16px 20px; background: #fff;
  border: 1px solid #e2ded7; border-radius: 12px; font-size: 16px;
}
.callout strong { color: #1d1d1f; }

pre {
  background: #1d1d1f; color: #e8e6e1; padding: 20px 22px;
  border-radius: 12px; overflow-x: auto; margin: 18px 0;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 13.5px; line-height: 1.6;
}
code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: .88em; background: #e8e4dd; padding: 2px 6px; border-radius: 5px;
}
pre code { background: none; padding: 0; font-size: inherit; color: inherit; }

table {
  width: 100%; border-collapse: collapse; margin: 20px 0;
  background: #fff; border-radius: 12px; overflow: hidden;
  font-size: 15px; box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
th, td { padding: 13px 16px; text-align: left; vertical-align: top; border-bottom: 1px solid #eeeae4; }
th { background: #faf8f5; font-weight: 650; font-size: 13px; letter-spacing: .03em; text-transform: uppercase; color: #6b665f; }
tr:last-child td { border-bottom: none; }

ol, ul { padding-left: 24px; margin: 14px 0; }
li { margin: 7px 0; }

hr { border: none; border-top: 1px solid #e2ded7; margin: 44px 0; }

.footer { margin-top: 60px; padding-top: 22px; border-top: 1px solid #ddd8d0; font-size: 13px; color: #8a857e; }

strong { font-weight: 650; }

@media (max-width: 600px) {
  body { font-size: 16px; }
  .hero { padding: 30px 20px 26px; border-radius: 14px; }
  .hero h1 { font-size: 27px; }
  h2 { font-size: 21px; margin-top: 38px; }
  pre { padding: 16px 14px; font-size: 12.5px; }
  th, td { padding: 10px 12px; font-size: 14px; }
  table { display: block; overflow-x: auto; }
}
"""


def md_inline(text):
    """Inline: code, bold, italic, links."""
    text = html.escape(text, quote=False)
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append("<code>" + p[1:-1] + "</code>")
            continue
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", p)
        p = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', p)
        out.append(p)
    return "".join(out)


def build(src_text):
    lines = src_text.split("\n")
    body = []
    i = 0
    n = len(lines)
    title = ""
    kicker = ""
    updated = ""
    list_mode = None  # 'ul' | 'ol'

    def close_list():
        nonlocal list_mode
        if list_mode:
            body.append(f"</{list_mode}>")
            list_mode = None

    while i < n:
        raw = lines[i]
        line = raw.rstrip()

        # frontmatter
        if line.strip() == "---" and i == 0:
            i += 1
            while i < n and lines[i].strip() != "---":
                if ":" in lines[i]:
                    k, v = lines[i].split(":", 1)
                    if k.strip() == "title":
                        title = v.strip()
                    if k.strip() == "updated":
                        updated = v.strip()
                i += 1
            i += 1
            continue

        if not line.strip():
            close_list()
            i += 1
            continue

        # hr
        if line.strip() == "---":
            close_list()
            body.append("<hr>")
            i += 1
            continue

        # code fence
        if line.strip().startswith("```"):
            close_list()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            body.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            continue

        # table
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?[\s:|-]+\|", lines[i + 1]):
            close_list()
            rows = [line]
            i += 2
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(lines[i])
                i += 1
            body.append("<table>")
            for ri, r in enumerate(rows):
                cells = [c.strip() for c in r.strip().strip("|").split("|")]
                tag = "th" if ri == 0 else "td"
                if ri == 0:
                    body.append("<thead><tr>")
                elif ri == 1:
                    body.append("<tbody><tr>")
                else:
                    body.append("<tr>")
                for c in cells:
                    body.append(f"<{tag}>{md_inline(c)}</{tag}>")
                body.append("</tr>")
                if ri == 0:
                    body.append("</thead>")
            body.append("</tbody></table>")
            continue

        # blockquote
        if line.strip().startswith(">"):
            close_list()
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            body.append("<blockquote><p>" + md_inline(" ".join(buf)) + "</p></blockquote>")
            continue

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            close_list()
            level = len(m.group(1))
            txt = m.group(2).strip()
            if level == 1:
                kicker = txt
            elif level == 2:
                body.append('<h2 class="section">' + md_inline(txt) + "</h2>")
            elif level == 3:
                body.append("<h3>" + md_inline(txt) + "</h3>")
            i += 1
            continue

        # ordered list
        m = re.match(r"^(\d+)\.\s+(.*)$", line)
        if m:
            if list_mode != "ol":
                close_list()
                body.append("<ol>")
                list_mode = "ol"
            body.append("<li>" + md_inline(m.group(2)) + "</li>")
            i += 1
            continue

        # unordered list
        m = re.match(r"^[-*]\s+(.*)$", line)
        if m:
            if list_mode != "ul":
                close_list()
                body.append("<ul>")
                list_mode = "ul"
            body.append("<li>" + md_inline(m.group(1)) + "</li>")
            i += 1
            continue

        # paragraph
        close_list()
        body.append("<p>" + md_inline(line.strip()) + "</p>")
        i += 1

    close_list()
    if not title:
        title = kicker or "Отчёт"

    doc = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<div class="hero">
<div class="kicker">ИИ-Консьерж · проект</div>
<h1>{html.escape(title)}</h1>
<p>Часть знаний консьержа — в Git-репозитории. Видно каждое изменение, откат в одну кнопку.</p>
<div class="meta"><span>Версия 0.1</span><span>Черновик для обсуждения</span><span>{html.escape(updated)}</span></div>
</div>
{chr(10).join(body)}
<div class="footer">ИИ-Консьерж · подготовлено для обсуждения</div>
</div>
</body>
</html>"""
    return doc


with open(SRC, encoding="utf-8") as f:
    src = f.read()

out = build(src)
with open(DST, "w", encoding="utf-8") as f:
    f.write(out)

print("OK", len(out), "bytes ->", DST)
