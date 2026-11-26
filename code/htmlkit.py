#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""htmlkit — сборщик HTML-отчётов в согласованном стиле (iPhone, чипы, спойлеры)."""

CSS = """
:root{--bg:#f4f2ee;--card:#fff;--ink:#1d1d1f;--mut:#6b665f;--line:#e2ded7;--soft:#faf8f5;--warn:#d9a41a;--ok:#2b7a4b}
[data-theme="dark"]{--bg:#0f0f10;--card:#1c1c1e;--ink:#f2f2f7;--mut:#98989f;--line:#333;--soft:#242426;--warn:#e0b446;--ok:#4aa06a}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Arial,sans-serif;
color:var(--ink);background:var(--bg);font-size:16px;line-height:1.62;-webkit-text-size-adjust:100%}
.wrap{max-width:820px;margin:0 auto;padding:0 12px 90px}
.bar{position:sticky;top:0;z-index:50;background:var(--bg);border-bottom:1px solid var(--line)}
.chips{display:flex;gap:7px;overflow-x:auto;padding:9px 12px 8px;scrollbar-width:none;-webkit-overflow-scrolling:touch;scroll-behavior:smooth}
.chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;padding:7px 13px;border-radius:999px;background:var(--soft);border:1px solid var(--line);
color:var(--mut);font-size:13px;font-weight:550;text-decoration:none;white-space:nowrap}
.chip:active{transform:scale(.96)}
.chip.on{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.switches{display:flex;gap:8px;padding:0 12px 9px;align-items:center}
.seg{display:flex;background:var(--soft);border:1px solid var(--line);border-radius:10px;padding:3px;gap:2px}
.seg button{border:0;background:transparent;color:var(--mut);font-size:12px;font-weight:600;
padding:6px 10px;border-radius:7px;font-family:inherit}
.seg button[aria-pressed="true"]{background:var(--card);color:var(--ink);box-shadow:0 1px 2px rgba(0,0,0,.12)}
.seg.push{margin-left:auto}
.allbtn{border:1px solid var(--line);background:var(--soft);color:var(--mut);font-size:12px;
font-weight:600;padding:6px 11px;border-radius:9px;font-family:inherit}
.hero{padding:22px 4px 4px}
.hero .k{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--mut);font-weight:600}
.hero h1{font-size:26px;line-height:1.18;margin:8px 0 0;letter-spacing:-.02em}
.hero p{color:var(--mut);font-size:14px;margin:8px 0 0}
[data-style="cards"] .sec{background:var(--card);border:1px solid var(--line);border-radius:16px;
padding:18px;margin:13px 0;box-shadow:0 1px 2px rgba(0,0,0,.05)}
[data-theme="dark"][data-style="cards"] .sec{box-shadow:none}
[data-style="cards"] h2{font-size:19px;margin:0;display:flex;gap:10px;align-items:center}
[data-style="cards"] h2::before{content:attr(data-n);font-size:12px;font-weight:700;background:var(--ink);
color:var(--bg);width:24px;height:24px;border-radius:7px;display:inline-flex;align-items:center;
justify-content:center;flex:0 0 24px}
[data-style="compact"] .sec{padding:13px 0 13px 15px;border-left:3px solid var(--line);margin:0 0 2px}
[data-style="compact"] h2{font-size:16px;margin:0}
[data-style="compact"] p,[data-style="compact"] li{font-size:14.5px;line-height:1.5}
h2{letter-spacing:-.01em}
p{margin:9px 0}
.mut{color:var(--mut);font-size:13.5px}
.sp{margin:11px 0 0;border-radius:12px;background:var(--soft);border:1px solid var(--line);overflow:hidden}
.sp>summary{list-style:none;cursor:pointer;padding:13px 14px;font-size:14.5px;font-weight:600;
display:flex;align-items:center;gap:9px}
.sp>summary::-webkit-details-marker{display:none}
.sp>summary::before{content:"+";width:20px;height:20px;flex:0 0 20px;border-radius:6px;background:var(--ink);
color:var(--bg);font-size:14px;font-weight:700;display:inline-flex;align-items:center;justify-content:center}
.sp[open]>summary::before{content:"\\2013"}
.sp>summary .t{flex:1}
.sp>summary .hint{font-size:10px;font-weight:700;color:var(--mut);text-transform:uppercase;letter-spacing:.06em}
.sp[open]>summary .hint{display:none}
.sp .in{padding:0 14px 15px;border-top:1px solid var(--line);font-size:14.5px}
.sp .in p:first-child{margin-top:12px}
.sp.tip{border-left:3px solid var(--warn)}
.thesis{font-size:15.5px;margin:0}
.flow{margin:13px 0 0}
.node{background:var(--soft);border:1px solid var(--line);border-radius:11px;padding:10px 12px;font-size:14px}
.node b{display:block;font-size:12.5px;margin-bottom:1px}
.arrow{text-align:center;color:var(--mut);font-size:14px;padding:3px 0}
table{width:100%;border-collapse:collapse;margin:10px 0;font-size:14px}
th,td{padding:9px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut);font-weight:650}
tr:last-child td{border-bottom:none}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.88em;background:var(--soft);
border:1px solid var(--line);padding:1px 5px;border-radius:5px}
pre{background:var(--ink);color:var(--bg);padding:14px 15px;border-radius:11px;overflow-x:auto;
font-size:12.5px;line-height:1.55}
pre code{background:none;border:0;padding:0;color:inherit}
ul,ol{padding-left:20px;margin:8px 0}
li{margin:4px 0}
.steps{counter-reset:s;margin:10px 0 0;padding:0;list-style:none}
.steps li{counter-increment:s;position:relative;padding-left:34px;margin:9px 0;font-size:14.5px}
.steps li::before{content:counter(s);position:absolute;left:0;top:1px;width:22px;height:22px;
border-radius:7px;background:var(--soft);border:1px solid var(--line);color:var(--mut);
font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center}
.badge{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
padding:2px 7px;border-radius:5px;background:var(--soft);border:1px solid var(--line);color:var(--mut)}
.badge.ok{color:var(--ok);border-color:var(--ok)}
.badge.warn{color:var(--warn);border-color:var(--warn)}
.footer{margin-top:26px;padding-top:16px;border-top:1px solid var(--line);font-size:12.5px;color:var(--mut)}
@media(max-width:420px){body{font-size:15.5px}.hero h1{font-size:23px}th,td{padding:8px 7px;font-size:13px}}
"""

JS = """
const root=document.documentElement;
const sp=document.querySelectorAll('details.sp');
const allBtn=document.getElementById('allBtn');
function setStyle(s){root.dataset.style=s;
 document.querySelectorAll('[data-s]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.s===s));}
function setTheme(t){root.dataset.theme=t;
 document.querySelectorAll('[data-t]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.t===t));}
document.querySelectorAll('[data-s]').forEach(b=>b.onclick=()=>setStyle(b.dataset.s));
document.querySelectorAll('[data-t]').forEach(b=>b.onclick=()=>setTheme(b.dataset.t));
let allOpen=false;
if(allBtn){allBtn.onclick=()=>{allOpen=!allOpen;sp.forEach(d=>d.open=allOpen);
 allBtn.textContent=allOpen?'Свернуть всё':'Раскрыть всё';};}
const chips=[...document.querySelectorAll('.chip')];
const secs=chips.map(c=>document.querySelector(c.getAttribute('href'))).filter(Boolean);
if('IntersectionObserver' in window){
 const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){
  chips.forEach(c=>c.classList.remove('on'));
  const c=chips.find(x=>x.getAttribute('href')==='#'+e.target.id);if(c)c.classList.add('on');}})},
  {rootMargin:'-70px 0px -70% 0px'});
 secs.forEach(s=>io.observe(s));
}
setStyle('cards');setTheme('light');
"""


def spoiler(title, html, tip=False, open_=False):
    cls = "sp tip" if tip else "sp"
    op = " open" if open_ else ""
    return ('<details class="%s"%s><summary><span class="t">%s</span>'
            '<span class="hint">показать</span></summary><div class="in">%s</div></details>'
            % (cls, op, title, html))


def page(title, kicker, subtitle, sections, footer=""):
    """sections: list of dicts {id, chip, title, html}"""
    chips = "".join('<a class="chip" href="#%s">%s</a>' % (s["id"], s["chip"]) for s in sections)
    body = []
    body.append('<div class="hero"><div class="k">%s</div><h1>%s</h1><p>%s</p></div>'
                % (kicker, title, subtitle))
    for i, s in enumerate(sections, 1):
        body.append('<div class="sec" id="%s"><h2 data-n="%d">%s</h2>%s</div>'
                    % (s["id"], i, s["title"], s["html"]))
    if footer:
        body.append('<div class="footer">%s</div>' % footer)
    sw = ("<div class=\"switches\">"
          "<div class=\"seg\" role=\"group\"><button data-s=\"cards\">Карточки</button>"
          "<button data-s=\"compact\">Компакт</button></div>"
          "<button class=\"allbtn\" id=\"allBtn\">Раскрыть всё</button>"
          "<div class=\"seg push\" role=\"group\"><button data-t=\"light\">Свет</button>"
          "<button data-t=\"dark\">Тьма</button></div></div>")
    return ("<!DOCTYPE html><html lang=\"ru\" data-style=\"cards\" data-theme=\"light\"><head>"
            "<meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, "
            "initial-scale=1, viewport-fit=cover\"><meta name=\"theme-color\" content=\"#f4f2ee\">"
            "<title>%s</title><style>%s</style></head><body><div class=\"bar\">"
            "<div class=\"chips\">%s</div>%s</div><div class=\"wrap\">%s</div>"
            "<script>%s</script></body></html>"
            % (title, CSS, chips, sw, "".join(body), JS))
