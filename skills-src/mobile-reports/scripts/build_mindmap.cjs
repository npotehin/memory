#!/usr/bin/env node
"use strict"
/*
 * MultiTool mind-map builder — «Швейцарская сетка» (Swiss grid, variant 1a).
 *
 * Reads a hierarchical outline JSON and writes ONE self-contained, interactive
 * .html mind map. The model writes the JSON only — no code generation.
 *
 * Design principle: a two-sided tree — root in the centre, branches running left
 * and right, their children a third column further out. Hierarchy is carried by
 * type size, weight and rules (lines), never by boxes, fills, shadows or radii.
 * The only colour besides ink and paper is the signal red, and it works purely as
 * a marker: branch number, year, branch underline, root's EN line.
 *
 * Three levels, no more. A fourth level is folded into the note line of its
 * level-2 node (done automatically here).
 *
 * Output references NO external assets (no CDN, fonts, images, network) — mandatory,
 * because it renders inside an offline, sandboxed preview iframe.
 *
 * JSON shape:
 *   {
 *     "title": "Первая мировая война",
 *     "en":    "World War I",
 *     "years": "1914—18",
 *     "branches": [
 *       { "num": "01", "side": "r", "ru": "Причины", "en": "Causes",
 *         "nodes": [
 *           { "ru": "Убийство Франца Фердинанда", "en": "Assassination",
 *             "year": "1914", "note": "28 июня, Сараево" }
 *         ] }
 *     ]
 *   }
 */
const fs = require("fs")

// ── layout metrics (px) — from the spec ──────────────────────────────────────
const CFG = {
  rootW: 240,
  rootH: 118, // only a floor for canvas height; the real root is measured
  w1: 172,
  w2: 252,
  g1: 44, // root → branch
  g2: 52, // branch → node
  gap: 14, // between nodes of one branch
  gg: 36, // between branch groups
  pad: 30, // horizontal canvas padding
}

const MAX_BRANCHES = 14
const MAX_NODES_PER_BRANCH = 24
const MAX_NODES = 400

// ── interface language ───────────────────────────────────────────────────────
// The map is written in ONE language — the user's. The chrome (title suffix, hint
// line, buttons) has to follow it, otherwise an English map ends up with Russian
// furniture. Languages we have strings for get the full chrome; anything else gets
// neutral, wordless chrome rather than borrowed English, so nothing is ever mixed.
const UI = {
  ru: {
    kind: "интеллект-карта",
    hint: "клик по ветви — свернуть · тяни — двигать · колесо — масштаб",
    fit: "по размеру",
    tOut: "Уменьшить",
    tIn: "Увеличить",
    tFit: "По размеру",
  },
  en: {
    kind: "mind map",
    hint: "click a branch to collapse · drag to pan · wheel to zoom",
    fit: "fit",
    tOut: "Zoom out",
    tIn: "Zoom in",
    tFit: "Fit to window",
  },
}
const UI_NEUTRAL = { kind: "", hint: "", fit: "100%", tOut: "", tIn: "", tFit: "" }
const uiFor = (lang) => UI[lang] || UI_NEUTRAL

const CYRILLIC = /[Ѐ-ӿ]/

// ── input normalisation ──────────────────────────────────────────────────────
const str = (v) => (v === undefined || v === null ? "" : String(v).trim())

// Level 4+ is not a level: fold descendant titles into the node's note.
function foldDeep(raw) {
  const kids = raw.nodes || raw.children || raw.kids
  if (!Array.isArray(kids) || kids.length === 0) return ""
  const parts = []
  for (const k of kids) {
    if (k === null || typeof k !== "object") continue
    const t = str(k.ru || k.title)
    if (t) parts.push(t)
    const deeper = foldDeep(k)
    if (deeper) parts.push(deeper)
  }
  return parts.join(" · ")
}

function normNode(raw) {
  if (raw === null || typeof raw !== "object" || Array.isArray(raw)) return null
  const ru = str(raw.ru || raw.title)
  if (!ru) return null
  let note = str(raw.note)
  const folded = foldDeep(raw)
  if (folded) note = note ? note + " · " + folded : folded
  return { ru, sub: str(raw.sub || raw.en), year: str(raw.year), note }
}

function normalize(raw) {
  if (raw === null || typeof raw !== "object" || Array.isArray(raw)) return null
  const title = str(raw.title || raw.ru)
  if (!title) return null

  const rawBranches = raw.branches || raw.children || raw.kids
  const branches = []
  let total = 0
  if (Array.isArray(rawBranches)) {
    for (const b of rawBranches) {
      if (b === null || typeof b !== "object") continue
      const ru = str(b.ru || b.title)
      if (!ru) continue
      if (branches.length >= MAX_BRANCHES) {
        console.error(`warn: more than ${MAX_BRANCHES} branches; the extra ones were dropped`)
        break
      }
      const rawKids = b.nodes || b.children || b.kids
      const nodes = []
      if (Array.isArray(rawKids)) {
        for (const k of rawKids) {
          const n = normNode(k)
          if (!n) continue
          if (nodes.length >= MAX_NODES_PER_BRANCH) {
            console.error(`warn: branch "${ru}" has more than ${MAX_NODES_PER_BRANCH} nodes; extra ones dropped`)
            break
          }
          if (total >= MAX_NODES) {
            console.error(`warn: hit the ${MAX_NODES}-node cap; remaining nodes dropped`)
            break
          }
          nodes.push(n)
          total++
        }
      }
      const side = str(b.side).toLowerCase() === "l" ? "l" : str(b.side).toLowerCase() === "r" ? "r" : ""
      branches.push({ ru, sub: str(b.sub || b.en), num: str(b.num), side, nodes })
    }
  }

  // Numbering falls back to reading order.
  branches.forEach((b, i) => {
    if (!b.num) b.num = String(i + 1).padStart(2, "0")
  })

  // Sides: honour explicit ones; otherwise balance by estimated HEIGHT.
  const anyExplicit = branches.some((b) => b.side)
  if (!anyExplicit) {
    const weight = (b) =>
      b.nodes.length === 0 ? 52 + CFG.gg : b.nodes.reduce((a, n) => a + (n.note ? 66 : 50) + CFG.gap, 0) + CFG.gg
    const order = branches.map((b, i) => ({ i, w: weight(b) })).sort((a, b) => b.w - a.w || a.i - b.i)
    let wr = 0,
      wl = 0
    for (const { i, w } of order) {
      if (wr <= wl) {
        branches[i].side = "r"
        wr += w
      } else {
        branches[i].side = "l"
        wl += w
      }
    }
  } else {
    for (const b of branches) if (!b.side) b.side = "r"
  }

  // Language: take it as given, otherwise infer it.
  let lang = str(raw.lang).toLowerCase().slice(0, 2)
  if (!lang) {
    const sample = [title, str(raw.sub || raw.en)]
      .concat(branches.map((b) => b.ru + " " + b.sub))
      .concat(branches.flatMap((b) => b.nodes.map((n) => n.ru + " " + n.sub + " " + n.note)))
      .join(" ")
    lang = CYRILLIC.test(sample) ? "ru" : "en"
  }

  return { title, sub: str(raw.sub || raw.en), years: str(raw.years), lang, branches }
}

// ── html emission ────────────────────────────────────────────────────────────
function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;")
}

const CSS = `
:root{
  --paper:#FBFAF7; --ink:#14130F; --ink60:rgba(20,19,15,.6); --ink45:rgba(20,19,15,.45);
  --rule:rgba(20,19,15,.22); --conn:rgba(20,19,15,.3); --accent:#D8231C;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;height:100%;background:var(--paper)}
body{font-family:'Helvetica Neue',Helvetica,sans-serif;-webkit-font-smoothing:antialiased;
     color:var(--ink);font-variant-numeric:tabular-nums}
::selection{background:rgba(216,35,28,.18)}

.app{position:fixed;inset:0;display:flex;flex-direction:column;background:var(--paper)}
.bar{flex:0 0 auto;display:flex;align-items:center;gap:16px;padding:14px 22px;border-bottom:1px solid var(--rule)}
.bar-years{font-size:11px;font-weight:700;color:var(--accent);white-space:nowrap;flex:0 0 auto}
.bar-title{font-size:14px;font-weight:700;letter-spacing:-.01em;white-space:nowrap;flex:0 0 auto}
.bar-en{font-size:9.5px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--ink45);
        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0;flex:0 1 auto}
.bar-sp{flex:1 1 auto;min-width:8px}
.bar-hint{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink45);
          white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0;flex:0 1 auto}
.btns{display:flex;border:1px solid var(--rule);flex:0 0 auto}
.btns button{font:inherit;font-weight:700;line-height:1;cursor:pointer;background:var(--paper);
             color:var(--ink);border:none;border-right:1px solid var(--rule);padding:8px 12px}
.btns button:last-child{border-right:none}
.btns button:hover{background:var(--ink);color:var(--paper)}
#zin,#zout{font-size:13px}
#rst{font-size:10px;letter-spacing:.1em;text-transform:uppercase}

.stage{flex:1 1 auto;position:relative;overflow:hidden;cursor:grab;touch-action:none}
.stage.grabbing{cursor:grabbing}
.canvas{position:absolute;left:0;top:0;transform-origin:0 0}
.root,.b,.n,.eh,.ev{position:absolute;left:0;top:0}

.root{width:240px;padding:16px 18px;background:var(--ink)}
.root-years{font-size:34px;font-weight:700;letter-spacing:-.04em;line-height:1;color:var(--paper)}
.root-title{margin:0;font-size:14px;font-weight:700;letter-spacing:-.01em;color:var(--paper);margin-top:8px}
.root-en{font-size:9.5px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);margin-top:4px}

.b{display:block;background:none;color:inherit;font:inherit;text-align:inherit;border:0;border-radius:0;outline-offset:4px;width:172px;cursor:pointer;padding-bottom:6px;border-bottom:2px solid var(--accent)}
.b-row{display:flex;align-items:baseline;gap:8px}
.b-num{font-size:11px;font-weight:700;color:var(--accent);flex:0 0 auto}
.b-ru{font-size:17px;font-weight:700;letter-spacing:-.02em;line-height:1.1}
.b-sign{font-size:12px;font-weight:700;color:var(--ink45);flex:0 0 auto}
.b-en{font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--ink45);margin-top:3px}

.n{width:252px;padding-top:7px;border-top:1px solid var(--rule)}
.n-row{display:flex;align-items:baseline;gap:7px}
.n-year{font-size:12px;font-weight:700;color:var(--accent);flex:0 0 auto}
.n-ru{font-size:13.5px;font-weight:700;line-height:1.2;letter-spacing:-.01em}
.n-en{font-size:10px;letter-spacing:.1em;text-transform:uppercase;line-height:1.3;color:var(--ink45);margin-top:3px}
.n-note{font-size:11px;line-height:1.35;color:var(--ink60);margin-top:3px}

.side-r{text-align:left}
.side-r .b-row,.side-r .n-row{justify-content:flex-start}
.side-l{text-align:right}
.side-l .b-row,.side-l .n-row{justify-content:flex-end}

.eh{height:1px;background:var(--conn)}
.ev{width:1px;background:var(--conn)}
.is-hidden{display:none}
`

const SCRIPT = `
(function(){
  var CFG=__CFG__;
  var stage=document.getElementById('stage'), canvas=document.getElementById('canvas');
  var edgeBox=document.getElementById('edges'), rootEl=document.querySelector('.root');
  var branches=[].slice.call(document.querySelectorAll('.b'));
  var collapsed={}, cw=0, ch=0, fit={s:1,x:0,y:0}, tr=null;

  branches.forEach(function(b){
    b.__kids=[].slice.call(document.querySelectorAll('.n[data-parent="'+b.getAttribute('data-id')+'"]'));
  });

  function clamp(s){ return Math.min(3, Math.max(0.25, s)); }
  function T(){ return tr || fit; }
  function applyView(){ var t=T();
    canvas.style.transform='translate('+t.x+'px,'+t.y+'px) scale('+t.s+')'; }

  // One orthogonal elbow = three 1px divs. No SVG.
  function elbow(x0,y0,x1,y1){
    var mid=(x0+x1)/2;
    var h1=document.createElement('div'); h1.className='eh';
    h1.style.width=Math.abs(mid-x0)+'px';
    h1.style.transform='translate('+Math.min(x0,mid)+'px,'+y0+'px)';
    var v=document.createElement('div'); v.className='ev';
    v.style.height=Math.abs(y1-y0)+'px';
    v.style.transform='translate('+mid+'px,'+Math.min(y0,y1)+'px)';
    var h2=document.createElement('div'); h2.className='eh';
    h2.style.width=Math.abs(x1-mid)+'px';
    h2.style.transform='translate('+Math.min(x1,mid)+'px,'+y1+'px)';
    edgeBox.appendChild(h1); edgeBox.appendChild(v); edgeBox.appendChild(h2);
  }

  function layout(){
    branches.forEach(function(b){
      var open=!collapsed[b.getAttribute('data-id')];
      b.setAttribute('aria-expanded', String(open));
      b.__kids.forEach(function(k){ k.classList.toggle('is-hidden', !open); });
      var sign=b.querySelector('.b-sign'); if(sign) sign.textContent=open?'\\u2212':'+';
    });

    var half=CFG.rootW/2+CFG.g1+CFG.w1+CFG.g2+CFG.w2+CFG.pad;
    cw=half*2; var cx=cw/2;

    var sides={r:{items:[],total:0}, l:{items:[],total:0}};
    ['r','l'].forEach(function(side){
      var cur=0, items=[];
      branches.filter(function(b){ return b.getAttribute('data-side')===side; }).forEach(function(b){
        var hb=b.offsetHeight, gs=cur, id=b.getAttribute('data-id');
        var kids=collapsed[id]?[]:b.__kids;
        if(kids.length===0){
          items.push({b:b, by:cur+hb/2, kids:[], ys:[]});
          cur=gs+hb;
        } else {
          var c=cur, ys=[];
          kids.forEach(function(k){ var h=k.offsetHeight; ys.push(c+h/2); c+=h+CFG.gap; });
          var span=(c-CFG.gap)-gs;
          if(span<hb){ var padY=(hb-span)/2; ys=ys.map(function(y){ return y+padY; }); span=hb; }
          items.push({b:b, by:(ys[0]+ys[ys.length-1])/2, kids:kids, ys:ys});
          cur=gs+span;
        }
        cur+=CFG.gg;
      });
      sides[side]={items:items, total:Math.max(0,cur-CFG.gg)};
    });

    var rootH=rootEl.offsetHeight||CFG.rootH;
    ch=Math.max(sides.r.total, sides.l.total, rootH+80)+70;
    var rootY=ch/2;

    canvas.style.width=cw+'px'; canvas.style.height=ch+'px';
    edgeBox.textContent='';
    rootEl.style.transform='translate('+(cx-CFG.rootW/2)+'px,'+rootY+'px) translateY(-50%)';

    ['r','l'].forEach(function(side){
      var d=sides[side], dy=(ch-d.total)/2, right=(side==='r');
      var x1=right?cx+CFG.rootW/2+CFG.g1:cx-CFG.rootW/2-CFG.g1-CFG.w1;
      var x2=right?x1+CFG.w1+CFG.g2:x1-CFG.g2-CFG.w2;
      var rootEdge=right?cx+CFG.rootW/2:cx-CFG.rootW/2;
      var bEdge=right?x1+CFG.w1:x1;
      d.items.forEach(function(it){
        var by=it.by+dy;
        elbow(rootEdge, rootY, right?x1:x1+CFG.w1, by);
        it.b.style.transform='translate('+x1+'px,'+by+'px) translateY(-50%)';
        it.kids.forEach(function(k,i){
          var y=it.ys[i]+dy;
          elbow(bEdge, by, right?x2:x2+CFG.w2, y);
          k.style.transform='translate('+x2+'px,'+y+'px) translateY(-50%)';
        });
      });
    });

    var vw=stage.clientWidth||1440, vh=stage.clientHeight||860;
    var s=Math.min(1,(vw-48)/cw,(vh-32)/ch);
    fit={s:s, x:(vw-cw*s)/2, y:(vh-ch*s)/2};
    applyView();
  }

  function zoomCenter(f){ var t=T(), ns=clamp(t.s*f);
    var px=(stage.clientWidth||1440)/2, py=(stage.clientHeight||860)/2;
    tr={s:ns, x:px-(px-t.x)*(ns/t.s), y:py-(py-t.y)*(ns/t.s)}; applyView(); }

  document.getElementById('zin').onclick=function(){ zoomCenter(1.18); };
  document.getElementById('zout').onclick=function(){ zoomCenter(1/1.18); };
  document.getElementById('rst').onclick=function(){ tr=null; layout(); };

  var DRAG_PX=3, drag=null;
  stage.addEventListener('pointerdown', function(e){
    drag={x:e.clientX, y:e.clientY, moved:false, captured:false,
          b:(e.target&&e.target.closest)?e.target.closest('.b'):null};
    stage.classList.add('grabbing');
  });
  stage.addEventListener('pointermove', function(e){
    if(!drag) return;
    var dx=e.clientX-drag.x, dy=e.clientY-drag.y;
    if(!drag.moved && Math.abs(dx)+Math.abs(dy)>DRAG_PX){
      drag.moved=true;
      if(!drag.captured){ try{ stage.setPointerCapture(e.pointerId); drag.captured=true; }catch(_){ } }
    }
    if(!drag.moved) return;
    drag.x=e.clientX; drag.y=e.clientY;
    var t=T(); tr={s:t.s, x:t.x+dx, y:t.y+dy}; applyView();
  });
  function endDrag(e){
    if(!drag) return;
    var d=drag; drag=null; stage.classList.remove('grabbing');
    if(d.captured&&e){ try{ stage.releasePointerCapture(e.pointerId); }catch(_){ } }
    if(!d.moved && d.b){
      var id=d.b.getAttribute('data-id');
      collapsed[id]=!collapsed[id];
      layout();
    }
  }
  branches.forEach(function(b){
    b.addEventListener('click', function(e){
      if(e.detail !== 0) return;
      var id=b.getAttribute('data-id'); collapsed[id]=!collapsed[id]; layout();
    });
  });
  stage.addEventListener('pointerup', endDrag);
  stage.addEventListener('pointercancel', endDrag);

  stage.addEventListener('wheel', function(e){
    e.preventDefault();
    var r=stage.getBoundingClientRect(), px=e.clientX-r.left, py=e.clientY-r.top;
    var t=T(), f=(e.deltaY<0)?1.12:1/1.12, ns=clamp(t.s*f);
    tr={s:ns, x:px-(px-t.x)*(ns/t.s), y:py-(py-t.y)*(ns/t.s)}; applyView();
  }, {passive:false});

  window.addEventListener('resize', function(){ layout(); });
  layout();
  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(layout).catch(function(){});
})();
`

function emitRoot(d) {
  const parts = ['<div class="root">']
  if (d.years) parts.push(`<div class="root-years">${esc(d.years)}</div>`)
  parts.push(`<h1 class="root-title">${esc(d.title)}</h1>`)
  if (d.sub) parts.push(`<div class="root-en">${esc(d.sub)}</div>`)
  parts.push("</div>")
  return parts.join("")
}

function emitBranch(b, i) {
  const side = b.side === "l" ? "side-l" : "side-r"
  const parts = [`<button type="button" class="b ${side}" aria-expanded="true" aria-label="${esc(b.ru)}" data-id="b${i}" data-side="${b.side}">`]
  parts.push('<div class="b-row">')
  parts.push(`<div class="b-num">${esc(b.num)}</div>`)
  parts.push(`<div class="b-ru">${esc(b.ru)}</div>`)
  parts.push('<div class="b-sign">−</div>')
  parts.push("</div>")
  if (b.sub) parts.push(`<div class="b-en">${esc(b.sub)}</div>`)
  parts.push("</button>")
  return parts.join("")
}

function emitNode(n, bi) {
  const side = n.__side === "l" ? "side-l" : "side-r"
  const parts = [`<div class="n ${side}" data-parent="b${bi}" data-side="${n.__side}">`]
  parts.push('<div class="n-row">')
  if (n.year) parts.push(`<div class="n-year">${esc(n.year)}</div>`)
  parts.push(`<div class="n-ru">${esc(n.ru)}</div>`)
  parts.push("</div>")
  if (n.sub) parts.push(`<div class="n-en">${esc(n.sub)}</div>`)
  if (n.note) parts.push(`<div class="n-note">${esc(n.note)}</div>`)
  parts.push("</div>")
  return parts.join("")
}

function buildHtml(d) {
  const ui = uiFor(d.lang)
  const caption = [d.sub, ui.kind].filter(Boolean).join(" · ")

  let nodesHtml = ""
  let branchesHtml = ""
  d.branches.forEach((b, i) => {
    branchesHtml += emitBranch(b, i)
    b.nodes.forEach((n) => {
      n.__side = b.side
      nodesHtml += emitNode(n, i)
    })
  })

  const script = SCRIPT.replace("__CFG__", JSON.stringify(CFG))

  const t = (s) => (s ? ` title="${esc(s)}"` : "")
  return (
    "<!DOCTYPE html>\n" +
    `<html lang="${esc(d.lang)}"><head><meta charset="utf-8">` +
    '<meta name="viewport" content="width=device-width, initial-scale=1">' +
    `<title>${esc(ui.kind ? d.title + " — " + ui.kind : d.title)}</title>` +
    `<style>${CSS}</style></head><body>` +
    '<div class="app">' +
    '<div class="bar">' +
    (d.years ? `<div class="bar-years">${esc(d.years)}</div>` : "") +
    `<div class="bar-title">${esc(d.title)}</div>` +
    (caption ? `<div class="bar-en">${esc(caption)}</div>` : "") +
    '<div class="bar-sp"></div>' +
    (ui.hint ? `<div class="bar-hint">${esc(ui.hint)}</div>` : "") +
    '<div class="btns">' +
    `<button id="zout"${t(ui.tOut)}>−</button>` +
    `<button id="rst"${t(ui.tFit)}>${esc(ui.fit)}</button>` +
    `<button id="zin"${t(ui.tIn)}>+</button>` +
    "</div></div>" +
    '<div class="stage" id="stage"><div class="canvas" id="canvas">' +
    '<div id="edges"></div>' +
    nodesHtml +
    branchesHtml +
    emitRoot(d) +
    "</div></div>" +
    "</div>" +
    `<script>${script.replace(/<\//g, "<\\/")}</script>` +
    "</body></html>\n"
  )
}

function main(argv) {
  if (argv.length !== 4) {
    console.error("usage: build_mindmap.cjs <mind-map.json> <output.html>")
    process.exit(2)
  }
  const specPath = argv[2],
    outPath = argv[3]
  let raw
  try {
    raw = JSON.parse(fs.readFileSync(specPath, "utf8"))
  } catch (e) {
    console.error(`failed to read ${specPath}: ${e.message}`)
    process.exit(1)
  }

  const data = normalize(raw)
  if (data === null) {
    console.error('error: the JSON must be one object with a non-empty "title"')
    process.exit(1)
  }
  if (data.branches.length === 0) {
    console.error('warn: no branches found — expected a "branches" array of objects with "ru" and "nodes"')
  }

  fs.writeFileSync(outPath, buildHtml(data), "utf8")
  console.log(`wrote ${outPath}`)
}

main(process.argv)
