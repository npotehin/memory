/*
 * ─────────────────────────────────────────────────────────────────────────
 *  ПРОИСХОЖДЕНИЕ: ОРИГИНАЛ, НЕ ИЗМЕНЁН
 *
 *  Автор: разработчик сервиса (каталог скиллов), не мы.
 *  Файл получен чтением из каталога и записан байт в байт.
 *  Правок не вносилось.
 *
 *  Изменённые версии лежат рядом, в ../scripts/ — там стоит своя пометка.
 *  Этот файл нужен для сверки: видно, что было до наших правок.
 * ─────────────────────────────────────────────────────────────────────────
 */
import json
import subprocess
import zipfile
from pathlib import Path


HELPERS = Path(__file__).resolve().parents[1] / "scripts"


def site(*args, check=True):
    return subprocess.run(["node", str(HELPERS / "site.cjs"), *map(str, args)],
                          capture_output=True, text=True, check=check)


def test_bundle_independent_html(tmp_path):
    source = tmp_path / "source"
    site("init", source)
    index = source / "index.html"
    html = index.read_text().replace("</body>", '<script src="counter.js"></script></body>')
    index.write_text(html)
    (source / "counter.js").write_text("document.title = 'Counter ready';")
    output = tmp_path / "counter.html"
    site("bundle", index, output)
    assert "Counter ready" in output.read_text()
    assert 'src="counter.js"' not in output.read_text()
    assert json.loads(site("check", output).stdout)["ok"]
    assert index.read_text() == html
    (source / "counter.js").unlink()
    assert site("bundle", index, tmp_path / "broken.html", check=False).returncode != 0
    assert not (tmp_path / "broken.html").exists()


def test_portable_directory_archive(tmp_path):
    source = tmp_path / "pages"
    site("init", source)
    archive = tmp_path / "pages.zip"
    site("archive", source, archive)
    with zipfile.ZipFile(archive) as zipped:
        assert zipped.read("pages/index.html") == (source / "index.html").read_bytes()


def test_mind_map_from_outline(tmp_path):
    outline = tmp_path / "outline.json"
    outline.write_text(json.dumps({"title": "Garden", "branches": [{"ru": "Herbs", "nodes": [{"ru": "Basil"}]}]}))
    html = tmp_path / "garden.html"
    subprocess.run(["node", str(HELPERS / "build_mindmap.cjs"), str(outline), str(html)], check=True)
    assert "Basil" in html.read_text()
    assert json.loads(site("check", html).stdout)["ok"]
