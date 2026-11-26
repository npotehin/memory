"use strict"
/**
 * parsers.cjs — замена закрытой папки vendor/parsers.cjs открытыми библиотеками.
 *
 * Было: один собранный файл на 640 КБ с парсерами HTML, JS, CSS и ZIP внутри.
 * Прочитать его целиком не удавалось — ответ инструмента обрезался, и скрипт
 * site.cjs не запускался.
 *
 * Стало: четыре обычных пакета с npm, каждый делает ровно одну работу.
 *
 *   parse5    разбор HTML по стандарту WHATWG — так же, как это делает браузер
 *   acorn     разбор JavaScript в дерево узлов
 *   postcss   разбор и пересборка CSS
 *   jszip     сборка ZIP-архивов
 *
 * Все четыре под MIT. Ставятся одной командой:
 *
 *   npm install parse5@8 acorn@8 postcss@8 jszip@3
 *
 * Скрипт ищет их в обычном порядке: сначала в node_modules рядом, потом в
 * глобальных. Если пакета нет — падает с понятным сообщением, а не с
 * «cannot find module».
 */

function need(name, hint) {
  try {
    return require(name)
  } catch (error) {
    const err = new Error(
      `Не хватает пакета «${name}». ${hint}\n` +
        `Установите: npm install parse5@8 acorn@8 postcss@8 jszip@3\n` +
        `Исходная ошибка: ${error.message}`
    )
    err.code = "MISSING_DEPENDENCY"
    throw err
  }
}

const parse5 = need("parse5", "Нужен для разбора HTML.")
const acorn = need("acorn", "Нужен для разбора JavaScript.")
const postcssModule = need("postcss", "Нужен для разбора CSS.")
const JSZip = need("jszip", "Нужен для сборки ZIP.")

const postcss = postcssModule.default || postcssModule

// ── HTML ────────────────────────────────────────────────────────────────────
// site.cjs ждёт объект с полем document, у которого есть querySelectorAll,
// querySelector, createElement и documentElement. parse5 отдаёт дерево узлов
// другого вида, поэтому оборачиваем его в тонкую обёртку с тем же интерфейсом.
function parseHTML(source) {
  const tree = parse5.parse(source, { sourceCodeLocationInfo: false })
  return { document: wrap(tree) }
}

const VOID = new Set([
  "area", "base", "br", "col", "embed", "hr", "img", "input",
  "link", "meta", "param", "source", "track", "wbr",
])

function wrap(node) {
  const el = {
    __node: node,
    get localName() {
      return node.tagName || ""
    },
    get attributes() {
      return node.attrs || []
    },
    hasAttribute(name) {
      return (node.attrs || []).some((a) => a.name === name)
    },
    getAttribute(name) {
      const found = (node.attrs || []).find((a) => a.name === name)
      return found ? found.value : null
    },
    setAttribute(name, value) {
      node.attrs = node.attrs || []
      const found = node.attrs.find((a) => a.name === name)
      if (found) found.value = value
      else node.attrs.push({ name, value: String(value) })
    },
    removeAttribute(name) {
      node.attrs = (node.attrs || []).filter((a) => a.name !== name)
    },
    get textContent() {
      return textOf(node)
    },
    set textContent(value) {
      node.childNodes = [{ nodeName: "#text", value: String(value) }]
    },
    get innerHTML() {
      return (node.childNodes || []).map(serialize).join("")
    },
    set innerHTML(value) {
      const parsed = parse5.parseFragment(value)
      node.childNodes = parsed.childNodes || []
    },
    get content() {
      // <template>: у parse5 содержимое лежит в node.content
      return wrap(node.content || { childNodes: [], tagName: "#template" })
    },
    get childNodes() {
      return node.childNodes || []
    },
    querySelectorAll(selector) {
      const out = []
      walkNodes(node, (n) => {
        if (matches(n, selector)) out.push(wrap(n))
      })
      return out
    },
    querySelector(selector) {
      let found = null
      walkNodes(node, (n) => {
        if (!found && matches(n, selector)) found = wrap(n)
      })
      return found
    },
    createElement(tagName) {
      return wrap({ nodeName: tagName, tagName, attrs: [], childNodes: [], __created: true })
    },
    createTextNode(text) {
      return { __text: String(text), nodeName: "#text" }
    },
    replaceWith(...args) {
      // site.cjs вызывает element.replaceWith(node) — заменяем сам узел.
      const parent = node.__parent
      if (!parent) return
      const replacement = args.length === 1 ? args[0] : args
      const index = parent.childNodes.indexOf(node)
      if (index === -1) return
      const incoming = (Array.isArray(replacement) ? replacement : [replacement]).map(unwrap)
      parent.childNodes.splice(index, 1, ...incoming)
    },
    appendChild(child) {
      node.childNodes = node.childNodes || []
      node.childNodes.push(unwrap(child))
    },
    removeChild(child) {
      node.childNodes = (node.childNodes || []).filter((n) => n !== unwrap(child))
    },
    get documentElement() {
      const html = (node.childNodes || []).find((n) => n.tagName === "html")
      return html ? wrap(html) : null
    },
    get document() {
      return el
    },
    createElementNS(_ns, tagName) {
      return wrap({ nodeName: tagName, tagName, attrs: [], childNodes: [], __created: true })
    },
    toString() {
      return serializeDocument(node)
    },
  }
  return el
}

function unwrap(el) {
  return el && el.__node ? el.__node : el
}

function textOf(node) {
  if (!node) return ""
  if (node.nodeName === "#text") return node.value || ""
  return (node.childNodes || []).map(textOf).join("")
}

function walkNodes(node, visit) {
  if (!node) return
  visit(node)
  for (const child of node.childNodes || []) {
    child.__parent = node
    walkNodes(child, visit)
    if (child.content) {
      child.content.__parent = node
      walkNodes(child.content, visit)
    }
  }
}

function serialize(node) {
  if (!node) return ""
  if (node.nodeName === "#documentType" || node.nodeName === "#doctype") {
    return `<!DOCTYPE ${node.name || "html"}>`
  }
  if (node.nodeName === "#text") return escapeText(node.value || "")
  if (!node.tagName) return (node.childNodes || []).map(serialize).join("")
  const attrs = (node.attrs || [])
    .map((a) => ` ${a.name}="${escapeAttr(a.value)}"`)
    .join("")
  const tag = node.tagName.toLowerCase()
  if (VOID.has(tag)) return `<${tag}${attrs}>`
  const inner = (node.childNodes || []).map(serialize).join("")
  return `<${tag}${attrs}>${inner}</${tag}>`
}

function replaceNode(target, replacement) {
  // Ищем родителя и подменяем узел в его списке детей.
  const parent = target.__parent
  if (!parent) return
  const idx = (parent.childNodes || []).indexOf(target.__node)
  if (idx === -1) return
  const nodes = Array.isArray(replacement) ? replacement.map(unwrap) : [unwrap(replacement)]
  parent.childNodes.splice(idx, 1, ...nodes)
}

function serializeDocument(node) {
  if (!node) return ""
  const parts = []
  for (const child of node.childNodes || []) {
    if (child.nodeName === "#documentType" || child.nodeName === "#doctype") {
      parts.push(`<!DOCTYPE ${child.name || "html"}>`)
    } else {
      parts.push(serialize(child))
    }
  }
  return parts.join("")
}

function escapeText(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
}

function escapeAttr(s) {
  return String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;")
}

// ── выбор элементов ─────────────────────────────────────────────────────────
// Поддерживаем только те селекторы, что реально встречаются в site.cjs:
// «tag», «tag[attr]», «tag1,tag2,tag3». Этого достаточно, а тащить сюда
// полноценный движок селекторов смысла нет.
function matches(node, selector) {
  if (!node || !node.tagName) return false
  const tag = node.tagName.toLowerCase()
  return selector.split(",").some((part) => {
    const piece = part.trim()
    if (!piece) return false
    const m = /^([a-z0-9-]+)?(?:\[([a-z0-9-]+)(?:=[^\]]+)?\])?$/i.exec(piece)
    if (!m) return false
    const [, wantTag, wantAttr] = m
    if (wantTag && tag !== wantTag.toLowerCase()) return false
    if (wantAttr && !(node.attrs || []).some((a) => a.name === wantAttr)) return false
    return true
  })
}

// ── JavaScript ──────────────────────────────────────────────────────────────
function parseJS(source, options = {}) {
  return acorn.parse(source, {
    ecmaVersion: options.ecmaVersion === "latest" ? "latest" : options.ecmaVersion || "latest",
    sourceType: options.sourceType || "script",
    allowReturnOutsideFunction: true,
    allowAwaitOutsideFunction: true,
    allowImportExportEverywhere: options.sourceType === "module",
  })
}

function walkJS(ast, visitors) {
  const stack = [ast]
  while (stack.length) {
    const node = stack.pop()
    if (!node || typeof node !== "object") continue
    if (node.type && visitors[node.type]) visitors[node.type](node)
    for (const key of Object.keys(node)) {
      if (key === "type" || key === "start" || key === "end" || key === "loc") continue
      const value = node[key]
      if (Array.isArray(value)) {
        for (const item of value) if (item && typeof item === "object") stack.push(item)
      } else if (value && typeof value === "object") {
        stack.push(value)
      }
    }
  }
}

// ── CSS ─────────────────────────────────────────────────────────────────────
// valueParser в оригинале разбирал значения вида url(...) и image-set(...).
// Здесь хватает регулярного разбора — этого достаточно для site.cjs.
function valueParser(value) {
  const nodes = []
  const re = /(url|image-set|-webkit-image-set)\(\s*(['"]?)([^'")]+)\2\s*\)/gi
  let last = 0
  let m
  while ((m = re.exec(value))) {
    if (m.index > last) nodes.push({ type: "text", value: value.slice(last, m.index) })
    nodes.push({
      type: "function",
      value: m[1],
      nodes: [{ type: "string", quote: m[2] || '"', value: m[3] }],
    })
    last = re.lastIndex
  }
  if (last < value.length) nodes.push({ type: "text", value: value.slice(last) })
  return {
    nodes,
    walk(visit) {
      for (const n of nodes) {
        if (n.type === "function") visit(n)
      }
    },
    toString() {
      return nodes
        .map((n) =>
          n.type === "function"
            ? `${n.value}(${(n.nodes || [])
                .map((c) => (c.type === "string" ? `${c.quote}${c.value}${c.quote}` : c.value))
                .join(", ")})`
            : n.value
        )
        .join("")
    },
  }
}

valueParser.stringify = (nodes) =>
  (nodes || [])
    .map((c) => (c.type === "string" ? `${c.quote}${c.value}${c.quote}` : c.value))
    .join(", ")

module.exports = {
  parseHTML,
  parseJS,
  walkJS,
  postcss,
  valueParser,
  JSZip,
}
