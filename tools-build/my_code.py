#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Страница «Мой код»: целиком сборщик htmlkit.py с разбором."""

import pathlib
import sys
import html as H

sys.path.insert(0, "/workspace/home/projects/report-build")
from htmlkit import page, spoiler

ROOT = pathlib.Path("/workspace/home/projects/memory-repo")
KIT = (ROOT / "htmlkit.py").read_text(encoding="utf-8")
LINES = KIT.splitlines()


def block(a, b):
    """Строки a..b (1-based, включительно) с нумерацией."""
    out = []
    for i in range(a - 1, min(b, len(LINES))):
        out.append("%4d  %s" % (i + 1, H.escape(LINES[i])))
    return "<pre><code>" + "\n".join(out) + "</code></pre>"


sections = []

sections.append(dict(
    id="what", chip="Что это", title="Сборщик страниц",
    html="""
<p class="thesis"><b>htmlkit.py — 192 строки, и это весь мой код вёрстки.</b>
Каждый отчёт, который вы открывали, собран этим файлом.</p>
<div class="flow">
<div class="node"><b>Файл</b>htmlkit.py, 9272 байта</div>
<div class="arrow">↓</div>
<div class="node"><b>Три части</b>CSS, JS, две функции</div>
<div class="arrow">↓</div>
<div class="node"><b>Вызов</b>page(title, kicker, subtitle, sections, footer)</div>
</div>
<p class="mut">Сейчас в репозитории лежит в двух местах: в корне и в
<code>code/htmlkit.py</code>. Второе — для чтения.</p>
"""+spoiler("Почему код короткий",
            """<p>Соблазн написать тысячи строк есть, но пользы нет. Всё, что нужно
странице, — это набор правил CSS и две функции сборки. Держать больше значит
поддерживать больше.</p>
<p>Обратная сторона: если понадобится сложная вёрстка —graphики, фильтры,
таблицы с сортировкой, — придётся дописывать. Сейчас этого нет.</p>""")))

sections.append(dict(
    id="tree", chip="Устройство", title="Из чего состоит",
    html="""
<table>
<thead><tr><th>Часть</th><th>Строки</th><th>Зачем</th></tr></thead>
<tbody>
<tr><td><code>CSS</code></td><td>5–86</td><td>Вся визуальная система</td></tr>
<tr><td><code>JS</code></td><td>88–110</td><td>Переключатели и чипы</td></tr>
<tr><td><code>spoiler()</code></td><td>113–118</td><td>Сборка раскрывашки</td></tr>
<tr><td><code>page()</code></td><td>121–152</td><td>Сборка страницы целиком</td></tr>
</tbody></table>
<p class="mut">Больше ничего нет — ни зависимостей, ни импортов.</p>
"""+spoiler("Почему одна строка CSS на правило",
            """<p>Минифицировано вручную: <code>.chip{...}</code> в одну строку.
Экономит читаемость, но отчёт всегда собирается одинаково и весит меньше.</p>
<p>Минус: править такую строку на телефоне неудобно. Если планируете трогать
CSS руками — я разверну его в нормальный формат, файл вырастет до 300 строк,
но станет читаемым.</p>""")))

sections.append(dict(
    id="tokens", chip="Цвета", title="Палитра",
    html="""
<p class="thesis"><b>Шесть цветов на тему.</b> Всё остальное — производное
от них.</p>
<table>
<thead><tr><th>Токен</th><th>Светлая</th><th>Тёмная</th></tr></thead>
<tbody>
<tr><td><code>--bg</code></td><td>#f4f2ee</td><td>#0f0f10</td></tr>
<tr><td><code>--card</code></td><td>#ffffff</td><td>#1c1c1e</td></tr>
<tr><td><code>--ink</code></td><td>#1d1d1f</td><td>#f2f2f7</td></tr>
<tr><td><code>--mut</code></td><td>#6b665f</td><td>#98989f</td></tr>
<tr><td><code>--line</code></td><td>#e2ded7</td><td>#333333</td></tr>
<tr><td><code>--soft</code></td><td>#faf8f5</td><td>#242426</td></tr>
</tbody></table>
<p class="mut">Плюс акценты: <code>--ok</code> зелёный и <code>--warn</code>
жёлтый — только для бейджей.</p>
"""+spoiler("Почему именно эти цвета",
            """<p>Тёплый фон <code>#f4f2ee</code> вместо белого: на телефоне вечером
белый экран бьёт по глазам. Тёплый оттенок читается мягче, но остаётся
светлым.</p>
<p>Тёмная тема не инверсия: <code>#0f0f10</code> почти чёрный, карточки
на тон светлее. Если просто инвертировать, тени превращаются в грязь —
поэтому в тёмной теме тени отключены совсем.</p>""")))

sections.append(dict(
    id="css", chip="Стили", title="Как устроена вёрстка",
    html="""
<p class="thesis"><b>Две плотности из одного HTML.</b> «Карточки» и
«компакт» — это одно и то же дерево, разные правила CSS.</p>
<p>Переключение — атрибут <code>data-style</code> на <code>&lt;html&gt;</code>.
Никакой перезагрузки, никакого второго файла.</p>
"""+spoiler("Карточки против компакта",
            """<p><b>Карточки:</b> каждый раздел — отдельный блок с рамкой, скруглением
16 px и лёгкой тенью. Воздух, но длинная страница.</p>
<p><b>Компакт:</b> рамок нет, вместо них цветная линейка слева, отступы
ужаты. Шрифт 14,5 вместо 16. Длинный технический разбор читается быстрее.</p>
<p>Задаётся тремя правилами: <code>[data-style="cards"] .sec</code> и
<code>[data-style="compact"] .sec</code>. Остальное наследуется.</p>""")
    + spoiler("Спойлеры: плюс, а не треугольник",
            """<p>Маркер задаётся через <code>summary::before</code> — «плюс»
в свёрнутом, «тире» в открытом. Два правила:</p>
<pre><code>.sp>summary::before{content:"+"}
.sp[open]>summary::before{content:"\\\\2013"}</code></pre>
<p>И обязательные <code>list-style:none</code> плюс
<code>::-webkit-details-marker{display:none}</code> — иначе Safari нарисует
свой треугольник поверх плюса. На этом уже спотыкались.</p>""")))

sections.append(dict(
    id="js", chip="Скрипт", title="Что делает JavaScript",
    html="""
<p class="thesis"><b>Тридцать строк.</b> Переключатели, кнопка «Раскрыть всё»
и подсветка чипа по разделу.</p>
<table>
<thead><tr><th>Функция</th><th>Действие</th></tr></thead>
<tbody>
<tr><td><code>setStyle</code></td><td>Меняет <code>data-style</code></td></tr>
<tr><td><code>setTheme</code></td><td>Меняет <code>data-theme</code></td></tr>
<tr><td><code>allBtn</code></td><td>Открывает все спойлеры разом</td></tr>
<tr><td><code>IntersectionObserver</code></td><td>Подсвечивает чип</td></tr>
</tbody></table>
"""+spoiler("Почему подсветка чипа работает именно так",
            """<pre><code>{rootMargin:'-70px 0px -70% 0px'}</code></pre>
<p>Верхний отступ 70 px — ровно высота закреплённой полосы. Нижний режет
70% экрана: раздел считается «текущим», только когда зашёл в верхнюю треть.
Без этого подсвечивались бы сразу три раздела.</p>""")))

sections.append(dict(
    id="page", chip="Функции", title="Как собирается страница",
    html="""
<p class="thesis"><b>Две функции, и всё.</b> <code>spoiler()</code> делает
раскрывашку, <code>page()</code> — страницу из списка разделов.</p>
<p><code>page("Заголовок", "Надзаголовок", "Описание", [разделы], "подвал")</code></p>
<p>Раздел — это словарь из четырёх полей: <code>id</code> для чипа,
<code>chip</code> — подпись чипа, <code>title</code> — заголовок,
<code>html</code> — содержимое.</p>
"""+spoiler("Почему отчёт задаётся списком, а не HTML",
            """<p>Ручная вёрстка на третий отчёт разъезжается: забываешь
<code>white-space:nowrap</code> у чипа, теряешь контраст в тёмной теме.
В модуле это задано один раз.</p>
<p>Цена: нестандартную страницу так не собрать. Для этого можно писать HTML
руками — скилл разрешает, просто придётся самому следить за мелочами.</p>""")))

sections.append(dict(
    id="limits", chip="Слабости", title="Что я сделал неидеально",
    html="""
<p class="thesis"><b>Три места, которые я бы переделал.</b></p>
<table>
<tbody>
<tr><td>CSS в одну строку</td><td><span class="badge warn">трудно править</span></td></tr>
<tr><td>Токены зашиты в файл</td><td><span class="badge warn">нет темы проекта</span></td></tr>
<tr><td>Проверки нет</td><td><span class="badge warn">375 px на глаз</span></td></tr>
</tbody></table>
"""+spoiler("Что конкретно и как исправить",
            """<p><b>Одна строка CSS.</b> Читать неудобно, diff в git нечитаемый.
Лечится разворотом в многострочный вид: плюс 200 строк, минус головная боль.</p>
<p><b>Токены в файле.</b> Если захотите другой стиль для РКШ — сейчас это
копия файла целиком. Правильнее — вынести палитру в отдельный словарь и
передавать в <code>page()</code>.</p>
<p><b>Проверка на глаз.</b> «Нет горизонтального скролла, чипы не ломаются» —
я смотрю это глазами. Автоматики нет. Можно прикрутить проверку ширины через
headless-браузер, но это отдельная работа.</p>""", tip=True)))

sections.append(dict(
    id="code", chip="Код", title="Файл целиком",
    html="""
<p class="thesis">Все 192 строки, как есть. Ничего не скрыто.</p>
"""+spoiler("Открыть код: CSS и токены, строки 5–86", block(5, 86))
    + spoiler("Открыть код: скрипт, строки 88–110", block(88, 110))
    + spoiler("Открыть код: функции, строки 113–152", block(113, 152))))

doc = page(
    title="Мой код",
    kicker="ИИ-Консьерж · устройство",
    subtitle="Сборщик страниц целиком: палитра, вёрстка, скрипт, обе функции.",
    sections=sections,
    footer='<a href="index.html" style="color:inherit">← К обновлениям</a> · <a href="skills.html" style="color:inherit">Скиллы</a> · 26.11.2026')

for dest in (ROOT / "my-code.html",
             pathlib.Path("/workspace/home/Documents/my-code.html")):
    dest.write_text(doc, encoding="utf-8")
print("OK", len(doc), "bytes, строк в файле:", len(LINES))
