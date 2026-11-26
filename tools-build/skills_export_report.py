#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Отчёт о ночной выгрузке скиллов в репозиторий памяти."""

import pathlib
import sys

sys.path.insert(0, "/workspace/home/projects/report-build")
from htmlkit import page, spoiler

ROOT = pathlib.Path("/workspace/home/projects/memory-repo")

ROWS = [
    ("mobile-reports", "Длинные материалы под телефон", 5, "до ночи"),
    ("spreadsheets", "Таблицы XLSX и CSV", 1, "до ночи"),
    ("data-analysis", "Анализ данных", 1, "до ночи"),
    ("presentations", "Презентации PPTX и HTML-слайды", 6, "A"),
    ("documents", "Word, PDF, формы", 8, "A"),
    ("source-research", "Разбор больших материалов", 9, "B"),
    ("news-briefing", "Новостные сводки", 6, "B"),
    ("shopping-research", "Подбор и сравнение товаров", 4, "B"),
    ("change-monitoring", "Слежение за изменениями", 5, "C"),
    ("tech-support", "Диагностика устройств и сети", 9, "C"),
    ("travel-leisure", "Поездки и досуг", 6, "C"),
    ("career-assistant", "Резюме и собеседования", 11, "D"),
    ("learning-support", "Учёба и конспекты", 5, "D"),
    ("personal-finance", "Личные финансы", 9, "D"),
    ("health-navigator", "Анализы и выписки", 9, "E"),
    ("fitness-progress", "Тренировки и прогресс", 8, "E"),
    ("food-planning", "Меню и закупка", 6, "E"),
    ("media-processing", "Нарезка и конвертация медиа", 9, "F"),
    ("video-audio", "Видео и звук", 17, "F"),
    ("video-production", "Сценарий и монтаж", 10, "F"),
]

TOTAL = sum(r[2] for r in ROWS)

sections = []

sections.append(dict(
    id="itog", chip="Итог", title="Что получилось",
    html="""
<p class="thesis"><b>20 скиллов в репозитории, %d файлов.</b> Выгрузка
прошла за одну ночь, каждый скилл отдельным коммитом.</p>
<div class="flow">
<div class="node"><b>20</b> скиллов выложено</div>
<div class="node"><b>1</b> пропущен — personal-apps, нет в каталоге</div>
<div class="node"><b>%d</b> файлов в skills-src/</div>
</div>
<p class="mut">Ветка main, последний коммит fb76612. Рабочая копия совпадает
с origin, неотправленного нет.</p>
""" % (len(ROWS) + 1, TOTAL)))

# таблица скиллов
rows_html = "".join(
    '<tr><td><code>%s</code></td><td>%s</td><td>%d</td></tr>' % (slug, name, n)
    for slug, name, n, batch in ROWS)
sections.append(dict(
    id="list", chip="Список", title="Все скиллы",
    html="""
<p class="thesis">Полный состав того, что теперь лежит в репозитории.</p>
<table><thead><tr><th>Скилл</th><th>Для чего</th><th>Файлов</th></tr></thead>
<tbody>%s</tbody></table>
""" % rows_html))

# что не переносилось
sections.append(dict(
    id="scope", chip="Границы", title="Что не попало",
    html="""
<p class="thesis"><b>Только текст.</b> Скрипты, тесты и код в репозиторий
не переносились — там инструкции, а не исполнение.</p>
<table>
<tbody>
<tr><td>SKILL.md</td><td><span class="badge ok">все</span></td></tr>
<tr><td>Справочники references/</td><td><span class="badge ok">все</span></td></tr>
<tr><td>Вложенные папки (ffmpeg)</td><td><span class="badge ok">сохранены</span></td></tr>
<tr><td>Файлы assets/*.json</td><td><span class="badge ok">перенесены</span></td></tr>
<tr><td>scripts/ и tests/</td><td><span class="badge warn">не переносились</span></td></tr>
</tbody></table>
"""+spoiler("Куда смотреть, если что-то не так",
            """<p>Журнал выгрузки — <code>skills-src/PROGRESS.md</code>. Там по строке
на каждый скилл: выложен или пропущен, и почему.</p>
<p>У <code>video-audio</code> 17 файлов — самый большой: одиннадцать
справочников плюс четыре файла про ffmpeg плюс схема раскадровки.</p>""")))

# страницы
sections.append(dict(
    id="pages", chip="Страницы", title="Публикация",
    html="""
<p class="thesis"><b>Страницы пока не пересобраны.</b> В репозитории лежат
исходники, HTML-каталог ждёт сборки.</p>
<table>
<tbody>
<tr><td>skills-src/</td><td><span class="badge ok">20 папок</span></td></tr>
<tr><td>skills.html</td><td><span class="badge warn">старая версия</span></td></tr>
<tr><td>skills/</td><td><span class="badge warn">3 страницы из 20</span></td></tr>
</tbody></table>
<p class="mut">Сборка назначена на 10:00: каталог, отдельные страницы,
проверка в браузере.</p>
"""))

doc = page(
    title="Выгрузка скиллов",
    kicker="ИИ-Консьерж · отчёт",
    subtitle="Что выложено в репозиторий памяти за ночь и что осталось сделать.",
    sections=sections,
    footer='<a href="index.html" style="color:inherit">← К обновлениям</a> · <a href="skills.html" style="color:inherit">Каталог скиллов</a> · 26.11.2026')

for dest in (ROOT / "skills-export-report.html",
             pathlib.Path("/workspace/home/Documents/skills-export-report.html")):
    dest.write_text(doc, encoding="utf-8")
print("OK", len(doc), "bytes")
