/*
 * ─────────────────────────────────────────────────────────────────────────
 *  ПРОИСХОЖДЕНИЕ: АВТОР — РАЗРАБОТЧИК СЕРВИСА. ЕСТЬ НАШИ ПРАВКИ.
 *
 *  Оригинал:  ../origin/site.cjs  (не изменён, для сверки)
 *  Правки:    одна строка: require("./vendor/parsers.cjs") → require("./parsers.cjs"), потом откат обратно
 *  Кто правил: ИИ-Консьерж, 26.11.2026
 *  Зачем:    сначала подключить открытые парсеры, затем вернуть как было
 * ─────────────────────────────────────────────────────────────────────────
 */
const fs = require("node:fs")
const path = require("node:path")
const http = require("node:http")
const { randomUUID } = require("node:crypto")
const { pipeline } = require("node:stream/promises")
const { Readable } = require("node:stream")
const { parseHTML, parseJS, walkJS, postcss, valueParser, JSZip } = require("./vendor/parsers.cjs")

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".htm": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json",
  ".pdf": "application/pdf",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".webp": "image/webp",
  ".avif": "image/avif",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
  ".otf": "font/otf",
  ".mp3": "audio/mpeg",
  ".wav": "audio/wav",
  ".ogg": "audio/ogg",
  ".mp4": "video/mp4",
  ".webm": "video/webm",
  ".vtt": "text/vtt",
}
const RESOURCES =
  "script,img[src],source[src],video[src],audio[src],track[src],video[poster],input[src],link[href],image,feimage,use"
const RESOURCE_LINKS = new Set(["stylesheet", "icon", "apple-touch-icon", "preload", "modulepreload"])

function resourceAttributes(element) {
  if (["image", "feimage", "use", "script"].includes(element.localName))
    return ["src", "href", "xlink:href"].filter((name) => element.hasAttribute(name))
  if (element.localName === "link") {
    return element
      .getAttribute("rel")
      ?.toLowerCase()
      .split(/\s+/)
      .some((rel) => RESOURCE_LINKS.has(rel))
      ? ["href"]
      : []
  }
  return ["src", "poster"].filter((name) => element.hasAttribute(name))
}

function select(root, selector) {
  return [
    ...root.querySelectorAll(selector),
    ...[...root.querySelectorAll("template")].flatMap((element) => select(element.content, selector)),
  ]
}

function saveTemplates(root) {
  root.querySelectorAll("template").forEach((element) => {
    saveTemplates(element.content)
    element.innerHTML = [...element.content.childNodes].map((node) => node.toString()).join("")
  })
}

function cssResources(value, visit) {
  const parsed = valueParser(value)
  parsed.walk((node) => {
    if (node.type !== "function") return
    if (["image-set", "-webkit-image-set"].includes(node.value.toLowerCase())) {
      node.nodes
        .filter((child) => child.type === "string")
        .forEach((child) => {
          child.value = visit(child.value)
        })
    }
    if (node.value.toLowerCase() !== "url") return
    const target = valueParser
      .stringify(node.nodes)
      .trim()
      .replace(/^(['"])([\s\S]*)\1$/, "$2")
    node.nodes = [{ type: "string", quote: '"', value: visit(target) }]
    return false
  })
  return parsed.toString()
}

function embedded(value) {
  return value.startsWith("data:") || value.startsWith("#")
}

function resolveAsset(value, base, root) {
  if (!value || /^[a-z][a-z\d+.-]*:|^\/\//i.test(value)) throw new Error(`Cannot embed external resource: ${value}`)
  const filename = fs.realpathSync(
    path.resolve(value.startsWith("/") ? root : base, decodeURIComponent(value.split(/[?#]/)[0]).replace(/^\//, "")),
  )
  if (filename !== root && !filename.startsWith(root + path.sep))
    throw new Error(`Resource is outside the source directory: ${value}`)
  return filename
}

function readAsset(value, base, root) {
  const filename = resolveAsset(value, base, root)
  return {
    filename,
    bytes: fs.readFileSync(filename),
    fragment: value.includes("#") ? value.slice(value.indexOf("#")) : "",
  }
}

function assetUrl(value, base, root) {
  if (embedded(value)) return value
  const asset = readAsset(value, base, root)
  const mime = MIME[path.extname(asset.filename).toLowerCase()]
  if (!mime) throw new Error(`Unsupported embedded asset type: ${value}`)
  return `data:${mime};base64,${asset.bytes.toString("base64")}${asset.fragment}`
}

function css(source, filename, root, ancestors = []) {
  if (ancestors.includes(filename)) throw new Error(`Circular CSS import: ${filename}`)
  const sheet = postcss.parse(source, { from: filename })
  sheet.walkAtRules(/^import$/i, (rule) => {
    const params = valueParser(rule.params).nodes.filter((node) => node.type !== "space" && node.type !== "comment")
    const target =
      params[0]?.type === "function" && params[0].value.toLowerCase() === "url"
        ? params[0].nodes[0]?.value
        : params[0]?.value
    if (!target || params.length !== 1) throw new Error(`Flatten conditional CSS imports before export: ${rule.params}`)
    const asset = readAsset(target, path.dirname(filename), root)
    rule.replaceWith(
      postcss.parse(css(asset.bytes.toString("utf8"), asset.filename, root, [...ancestors, filename])).nodes,
    )
  })
  sheet.walkDecls((declaration) => {
    declaration.value = cssResources(declaration.value, (target) => assetUrl(target, path.dirname(filename), root))
  })
  return sheet.toString()
}

function checkJS(source, type, report, location, visitImport) {
  if (type && !["module", "text/javascript", "application/javascript"].includes(type)) return
  try {
    walkJS(parseJS(source, { ecmaVersion: "latest", sourceType: type === "module" ? "module" : "script" }), {
      ImportDeclaration(node) {
        if (visitImport) return visitImport(node.source.value)
        report.errors.push(`${location}: build JavaScript imports before HTML export (${node.source.value})`)
      },
      ExportNamedDeclaration(node) {
        if (node.source && visitImport) return visitImport(node.source.value)
        if (node.source) report.errors.push(`${location}: unresolved module export (${node.source.value})`)
      },
      ExportAllDeclaration(node) {
        if (visitImport) return visitImport(node.source.value)
        report.errors.push(`${location}: unresolved module export (${node.source.value})`)
      },
      ImportExpression(node) {
        if (visitImport) {
          if (node.source.type === "Literal" && typeof node.source.value === "string")
            return visitImport(node.source.value)
          report.warnings.push(`${location}: verify computed dynamic imports in the browser`)
          return
        }
        if (
          node.source.type !== "Literal" ||
          typeof node.source.value !== "string" ||
          !node.source.value.startsWith("data:")
        ) {
          report.errors.push(`${location}: build dynamic imports before HTML export`)
        }
      },
    })
  } catch (error) {
    report.errors.push(`${location}: ${error.message}`)
  }
}

function checkMetadata(source, document, report) {
  if (!/^\s*<!doctype\s+html[\s>]/i.test(source)) report.errors.push("Add <!doctype html>")
  if (!document.documentElement?.getAttribute("lang")) report.errors.push("Set the page language on <html lang=…>")
  if (!document.querySelector("title")?.textContent.trim()) report.errors.push("Add a non-empty page title")
  if (!document.querySelector('meta[name="viewport"]')) report.errors.push("Add a viewport meta tag for mobile layout")
  if (select(document, "base[href]").length)
    report.errors.push("Remove <base href>; the artifact must not depend on another origin")
}

function checkHtml(source) {
  const document = parseHTML(source).document
  const report = {
    ok: true,
    bytes: Buffer.byteLength(source),
    errors: [],
    warnings: [],
  }
  checkMetadata(source, document, report)
  select(document, RESOURCES).forEach((element) => {
    resourceAttributes(element).forEach((attribute) => {
      const value = element.getAttribute(attribute)
      if (value && (!embedded(value) || (element.localName === "use" && !value.startsWith("#"))))
        report.errors.push(`Unembedded resource: ${element.localName}[${attribute}]=${value}`)
    })
  })
  select(document, "[srcset]").forEach((element) =>
    report.errors.push(`Replace ${element.localName}[srcset] with an embedded src before export`),
  )
  select(document, "iframe,object,embed").forEach((element) =>
    report.errors.push(`Standalone export does not support <${element.localName}>`),
  )
  select(document, "script")
    .filter((element) => !resourceAttributes(element).length)
    .forEach((element, index) =>
      checkJS(element.textContent, element.getAttribute("type"), report, `script ${index + 1}`),
    )
  select(document, "style,[style]").forEach((element) => {
    try {
      const sheet = postcss.parse(
        element.localName === "style" ? element.textContent : `x{${element.getAttribute("style")}}`,
      )
      sheet.walkAtRules(/^import$/i, (rule) => report.errors.push(`Unembedded CSS import: ${rule.params}`))
      sheet.walkDecls((declaration) =>
        cssResources(declaration.value, (target) => {
          if (target && !embedded(target)) report.errors.push(`Unembedded CSS resource: ${target}`)
          return target
        }),
      )
    } catch (error) {
      report.errors.push(`CSS: ${error.message}`)
    }
  })
  if (!document.querySelector("h1")) report.warnings.push("Check that the page has a clear primary heading")
  report.ok = report.errors.length === 0
  return report
}

function directoryFiles(root, directory = root) {
  return fs
    .readdirSync(directory)
    .sort()
    .flatMap((name) => {
      if (name === ".DS_Store") return []
      if ([".git", "node_modules"].includes(name) || /^\.env(?:\.|$)/i.test(name))
        throw new Error(`Use a clean export directory without ${name}`)
      const filename = path.join(directory, name)
      const stat = fs.lstatSync(filename)
      if (stat.isSymbolicLink()) throw new Error(`Copy real assets instead of symlinks: ${filename}`)
      if (stat.isDirectory()) return directoryFiles(root, filename)
      if (!stat.isFile()) throw new Error(`Unsupported export entry: ${filename}`)
      return [{ filename, relative: path.relative(root, filename).split(path.sep).join("/"), bytes: stat.size }]
    })
}

function srcsetTargets(source) {
  const targets = []
  let rest = source.trim()
  while (rest) {
    rest = rest.replace(/^[\s,]+/, "")
    if (!rest) break
    const target = /^\S+/.exec(rest)[0]
    targets.push(target.replace(/,+$/, ""))
    rest = rest.slice(target.length)
    if (!target.endsWith(",")) rest = rest.replace(/^[^,]*(?:,|$)/, "")
  }
  return targets
}

function checkDirectory(directory) {
  const root = fs.realpathSync(path.resolve(directory))
  const files = directoryFiles(root)
  const pages = files.filter((file) => /\.html?$/i.test(file.relative))
  const report = {
    ok: true,
    directory: root,
    bytes: files.reduce((sum, file) => sum + file.bytes, 0),
    files: files.length,
    pages: pages.map((file) => file.relative),
    errors: [],
    warnings: [],
  }
  if (!files.some((file) => file.relative === "index.html")) report.errors.push("Add an index.html entry page")
  const visit = (value, filename, navigation = false) => {
    if (!value || embedded(value)) return
    if (/^[a-z][a-z\d+.-]*:|^\/\//i.test(value)) {
      if (navigation) report.warnings.push(`${path.relative(root, filename)}: external navigation link ${value}`)
      if (!navigation) report.errors.push(`${path.relative(root, filename)}: remote resource ${value}`)
      return
    }
    if (value.startsWith("/") || value.includes("\\")) {
      report.errors.push(`${path.relative(root, filename)}: use portable relative paths: ${value}`)
      return
    }
    try {
      const stat = fs.statSync(resolveAsset(value, path.dirname(filename), root))
      if (!stat.isFile()) report.errors.push(`${path.relative(root, filename)}: link must name a file: ${value}`)
    } catch (error) {
      report.errors.push(`${path.relative(root, filename)}: ${value}: ${error.message}`)
    }
  }
  const checkSheet = (source, filename) => {
    try {
      const sheet = postcss.parse(source, { from: filename })
      sheet.walkAtRules(/^import$/i, (rule) => {
        const first = valueParser(rule.params).nodes.find((node) => !["space", "comment"].includes(node.type))
        const target = first?.type === "function" ? first.nodes[0]?.value : first?.value
        if (target) visit(target, filename)
        if (!target) report.errors.push(`${path.relative(root, filename)}: invalid CSS import`)
      })
      sheet.walkDecls((declaration) =>
        cssResources(declaration.value, (target) => {
          visit(target, filename)
          return target
        }),
      )
    } catch (error) {
      report.errors.push(`${path.relative(root, filename)}: CSS: ${error.message}`)
    }
  }
  const inspectJS = (source, type, filename) =>
    checkJS(source, type, report, path.relative(root, filename), (target) => {
      if (!embedded(target) && !target.startsWith("./") && !target.startsWith("../")) {
        report.errors.push(`${path.relative(root, filename)}: build or localize module import: ${target}`)
        return
      }
      visit(target, filename)
      report.warnings.push("JavaScript modules may require loopback HTTP; verify the promised launch mode")
    })
  pages.forEach((file) => {
    const source = fs.readFileSync(file.filename, "utf8")
    const document = parseHTML(source).document
    const metadata = { errors: [] }
    checkMetadata(source, document, metadata)
    report.errors.push(...metadata.errors.map((error) => `${file.relative}: ${error}`))
    select(document, RESOURCES).forEach((element) =>
      resourceAttributes(element).forEach((attribute) => visit(element.getAttribute(attribute), file.filename)),
    )
    select(document, "[srcset]").forEach((element) =>
      srcsetTargets(element.getAttribute("srcset")).forEach((target) => visit(target, file.filename)),
    )
    select(document, "a[href],area[href]").forEach((element) =>
      visit(element.getAttribute("href"), file.filename, true),
    )
    select(document, "iframe[src],object[data],embed[src]").forEach((element) =>
      visit(element.getAttribute(element.localName === "object" ? "data" : "src"), file.filename),
    )
    select(document, "script")
      .filter((element) => !resourceAttributes(element).length)
      .forEach((element) => inspectJS(element.textContent, element.getAttribute("type"), file.filename))
    select(document, "style,[style]").forEach((element) =>
      checkSheet(
        element.localName === "style" ? element.textContent : `x{${element.getAttribute("style")}}`,
        file.filename,
      ),
    )
  })
  files
    .filter((file) => /\.css$/i.test(file.relative))
    .forEach((file) => checkSheet(fs.readFileSync(file.filename, "utf8"), file.filename))
  files
    .filter((file) => /\.(?:m?js)$/i.test(file.relative))
    .forEach((file) => inspectJS(fs.readFileSync(file.filename, "utf8"), "module", file.filename))
  report.warnings = [...new Set(report.warnings)]
  report.ok = report.errors.length === 0
  return report
}

async function archive(directory, output) {
  const report = checkDirectory(directory)
  if (!report.ok) throw new Error(report.errors.join("\n"))
  const target = path.resolve(output)
  if (target.startsWith(report.directory + path.sep))
    throw new Error("Choose an archive path outside the export directory")
  if (fs.existsSync(target)) throw new Error("Choose a new archive path; existing archive was not changed")
  const files = directoryFiles(report.directory).map((file) => ({
    ...file,
    entry: `${path.basename(report.directory)}/${file.relative}`,
  }))
  const zipBytes = files.reduce((sum, file) => {
    const length = Buffer.byteLength(file.entry)
    const unicodeExtra = length === file.entry.length ? 0 : 9 + length
    return sum + file.bytes + 92 + 2 * (length + unicodeExtra)
  }, 22)
  if (files.length >= 65535 || zipBytes >= 0xffffffff)
    throw new Error("This export needs a ZIP64-capable archiver; the portable directory remains usable")
  fs.mkdirSync(path.dirname(target), { recursive: true })
  if (
    fs.realpathSync(path.dirname(target)).startsWith(report.directory + path.sep) ||
    fs.realpathSync(path.dirname(target)) === report.directory
  )
    throw new Error("Choose an archive path outside the export directory")
  const zip = new JSZip()
  files.forEach((file) =>
    zip.file(
      file.entry,
      Readable.from(
        (async function* () {
          for await (const chunk of fs.createReadStream(file.filename)) yield chunk
        })(),
        { objectMode: false },
      ),
      { createFolders: false },
    ),
  )
  const temporary = `${target}.${randomUUID()}.tmp`
  try {
    await pipeline(
      zip.generateNodeStream({ type: "nodebuffer", streamFiles: true, platform: "UNIX" }),
      fs.createWriteStream(temporary, { flags: "wx" }),
    )
    try {
      fs.linkSync(temporary, target)
    } catch {
      fs.copyFileSync(temporary, target, fs.constants.COPYFILE_EXCL)
    }
  } finally {
    fs.rmSync(temporary, { force: true })
  }
  return { ...report, archive: target, archiveBytes: fs.statSync(target).size }
}

function bundle(input, output) {
  const filename = fs.realpathSync(path.resolve(input))
  const root = path.dirname(filename)
  const document = parseHTML(fs.readFileSync(filename, "utf8")).document
  select(document, "link[href]")
    .filter((element) => element.getAttribute("rel")?.toLowerCase().split(/\s+/).includes("stylesheet"))
    .forEach((element) => {
      const asset = readAsset(element.getAttribute("href"), root, root)
      const replacement = document.createElement("style")
      if (element.hasAttribute("media")) replacement.setAttribute("media", element.getAttribute("media"))
      replacement.textContent = css(asset.bytes.toString("utf8"), asset.filename, root).replace(
        /<\/style/gi,
        "<\\/style",
      )
      element.replaceWith(replacement)
    })
  select(document, "script")
    .filter((element) => resourceAttributes(element).length)
    .forEach((element) => {
      if (
        element.getAttribute("type") !== "module" &&
        (element.hasAttribute("defer") || element.hasAttribute("async"))
      ) {
        throw new Error(
          "Move deferred/async classic scripts to the end of <body> before export; inlining them would change execution order",
        )
      }
      const asset = readAsset(element.getAttribute(resourceAttributes(element)[0]), root, root)
      resourceAttributes(element).forEach((attribute) => element.removeAttribute(attribute))
      element.removeAttribute("crossorigin")
      element.removeAttribute("integrity")
      element.textContent = asset.bytes.toString("utf8").replace(/<\/script/gi, "<\\/script")
    })
  select(document, "style").forEach((element) => {
    element.textContent = css(element.textContent, filename, root).replace(/<\/style/gi, "<\\/style")
  })
  select(document, "[style]").forEach((element) => {
    const sheet = css(`x{${element.getAttribute("style")}}`, filename, root)
    element.setAttribute("style", sheet.slice(sheet.indexOf("{") + 1, sheet.lastIndexOf("}")))
  })
  select(document, RESOURCES).forEach((element) => {
    resourceAttributes(element).forEach((attribute) => {
      const value = element.getAttribute(attribute)
      if (element.localName === "use" && !value.startsWith("#"))
        throw new Error("Inline SVG symbols and use a local #fragment before export")
      element.setAttribute(attribute, assetUrl(value, root, root))
    })
  })
  saveTemplates(document)
  const source = document.toString()
  const report = checkHtml(source)
  if (!report.ok) throw new Error(report.errors.join("\n"))
  if (path.resolve(output) === filename || (fs.existsSync(output) && fs.realpathSync(output) === filename))
    throw new Error("Keep the editable source: choose a different output HTML path")
  fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true })
  fs.writeFileSync(output, source)
  return { ...report, file: path.resolve(output) }
}

function init(directory, template = "html") {
  if (!["html", "react"].includes(template)) throw new Error("Choose --template html or react")
  const target = path.resolve(directory)
  if (fs.existsSync(target) && fs.readdirSync(target).length)
    throw new Error("Choose a new or empty directory; existing source was not changed")
  fs.mkdirSync(target, { recursive: true })
  const source = path.join(__dirname, "templates", template)
  function copyTemplate(from, to) {
    for (const entry of fs.readdirSync(from, { withFileTypes: true })) {
      const input = path.join(from, entry.name)
      const output = path.join(to, entry.name)
      if (entry.isDirectory()) {
        fs.mkdirSync(output)
        copyTemplate(input, output)
      } else if (entry.isFile()) {
        fs.writeFileSync(output, fs.readFileSync(input), { flag: "wx" })
      } else {
        throw new Error("Unsupported template entry: " + entry.name)
      }
    }
  }
  copyTemplate(source, target)
  return { directory: target, template, entry: path.join(target, "index.html"), needsInstall: template === "react" }
}

function preview(filename, port = 0) {
  const target = fs.realpathSync(path.resolve(filename))
  const directory = fs.statSync(target).isDirectory()
  if (!Number.isInteger(port) || port < 0 || port > 65535)
    throw new Error("Port must be an integer between 0 and 65535")
  const server = http.createServer((request, response) => {
    if (!["GET", "HEAD"].includes(request.method)) {
      response.writeHead(405).end()
      return
    }
    if (!directory && request.url !== "/" && request.url !== "/index.html") {
      response.writeHead(404).end()
      return
    }
    const resource = (() => {
      try {
        if (!directory) return fs.realpathSync(target)
        const pathname = decodeURIComponent(new URL(request.url, "http://127.0.0.1").pathname)
        if (pathname.includes("\\")) return
        const resolved = fs.realpathSync(path.join(target, pathname.endsWith("/") ? `${pathname}index.html` : pathname))
        if (!resolved.startsWith(target + path.sep)) return
        return resolved
      } catch {
        return
      }
    })()
    if (!resource || !fs.statSync(resource).isFile()) {
      response.writeHead(404).end()
      return
    }
    const size = fs.statSync(resource).size
    const range = request.headers.range && /^bytes=(\d*)-(\d*)$/.exec(request.headers.range)
    const start = range?.[1] ? Number(range[1]) : range?.[2] ? Math.max(0, size - Number(range[2])) : 0
    const end = range?.[1] && range[2] ? Math.min(size - 1, Number(range[2])) : size - 1
    if (
      request.headers.range &&
      (!range ||
        !(range[1] || range[2]) ||
        start > end ||
        start >= size ||
        (range[2] && Number(range[2]) === 0 && !range[1]))
    ) {
      response.writeHead(416, { "Content-Range": `bytes */${size}` }).end()
      return
    }
    response.writeHead(range ? 206 : 200, {
      "Content-Type": MIME[path.extname(resource).toLowerCase()] ?? "application/octet-stream",
      "Cache-Control": "no-store",
      "Accept-Ranges": "bytes",
      "Content-Length": range ? end - start + 1 : size,
      ...(range ? { "Content-Range": `bytes ${start}-${end}/${size}` } : {}),
    })
    if (request.method === "HEAD" || !size) return response.end()
    fs.createReadStream(resource, { start, end })
      .on("error", () => response.destroy())
      .pipe(response)
  })
  server.listen(port, "127.0.0.1", () =>
    console.log(JSON.stringify({ url: `http://127.0.0.1:${server.address().port}`, file: target })),
  )
  return server
}

module.exports = { init, bundle, checkHtml, checkDirectory, archive, preview }

async function main(args) {
  if (args[0] === "init" && args[1] && (args.length === 2 || (args.length === 4 && args[2] === "--template")))
    return console.log(JSON.stringify(init(args[1], args[3])))
  if (args[0] === "bundle" && args.length === 3) return console.log(JSON.stringify(bundle(args[1], args[2])))
  if (args[0] === "archive" && args.length === 3) return console.log(JSON.stringify(await archive(args[1], args[2])))
  if (args[0] === "check-directory" && args.length === 2) {
    const report = checkDirectory(args[1])
    console.log(JSON.stringify(report))
    if (!report.ok) process.exitCode = 1
    return
  }
  if (args[0] === "check" && args.length === 2) {
    const report = checkHtml(fs.readFileSync(args[1], "utf8"))
    console.log(JSON.stringify(report))
    if (!report.ok) process.exitCode = 1
    return
  }
  if (args[0] === "preview" && args[1] && (args.length === 2 || (args.length === 4 && args[2] === "--port")))
    return preview(args[1], args[3] === undefined ? 0 : Number(args[3])).on("error", (error) => {
      console.error(error.message)
      process.exitCode = 1
    })
  throw new Error(
    "Usage: site.cjs init DIR [--template html|react] | bundle INPUT.html OUTPUT.html | check FILE.html | check-directory DIR | archive DIR OUTPUT.zip | preview FILE.html|DIR [--port PORT]",
  )
}

if (require.main === module) {
  main(process.argv.slice(2)).catch((error) => {
    console.error(error.message)
    process.exitCode = 1
  })
}
