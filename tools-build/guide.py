#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pathlib
import sys
sys.path.insert(0, "/workspace/home/projects/report-build")
from htmlkit import page, spoiler

sections = []

sections.append(dict(
    id="s1", chip="Итог", title="Что предлагаю",
    html="""
<p class="thesis"><b>Один вход с вашей стороны — и дальше всё делаю сам.</b>
Вам не нужно лазить в GitHub и подтверждать. Вы один раз заходите на моём удалённом
браузере через экран, сессия сохраняется, и я работаю уже внутри неё.</p>
<p class="mut">Плюс два токена: GitHub (узкий) и Cloudflare (для Pages).</p>
<div class="flow">
  <div class="node"><b>Вы</b>один вход на экране · 5 минут</div>
  <div class="arrow">↓</div>
  <div class="node"><b>Я</b>репозиторий, коммиты, пуш, деплой</div>
  <div class="arrow">↓</div>
  <div class="node"><b>Результат</b>вы открываете и смотрите</div>
</div>
"""))

sections.append(dict(
    id="s2", chip="Что нужно", title="Три вещи от вас",
    html="""
<table>
<thead><tr><th>Что</th><th>Зачем</th><th>Сколько</th></tr></thead>
<tbody>
<tr><td><b>Вход в GitHub</b> на моём экране</td><td>Чтобы я коммитил и пушил от вашего имени</td><td>5 мин, один раз</td></tr>
<tr><td><b>Токен GitHub</b><br><span class="mut">fine-grained</span></td><td>Работа без вашего участия после входа</td><td>2 мин</td></tr>
<tr><td><b>Токен Cloudflare</b><br><span class="mut">+ Account ID</span></td><td>Публикация на Pages</td><td>3 мин</td></tr>
</tbody>
</table>
<p class="mut">Пароли и коды подтверждения в чат не присылайте — я их не принимаю и не храню.</p>
"""))

sections.append(dict(
    id="s3", chip="Вход", title="Шаг 1. Вход в GitHub",
    html="""
<p class="thesis">Вы заходите сами — на моём удалённом браузере, через живую ссылку на экран.
Я в это время не подглядываю пароль.</p>
<ol class="steps">
<li>Я открываю экран и присылаю вам ссылку.</li>
<li>Вы на телефоне или компьютере открываете её и видите браузер.</li>
<li>Входите в GitHub как обычно: логин, пароль.</li>
<li>Если GitHub просит код — он приходит вам на почту. Вводите его <b>на экране</b>, не в чат.</li>
<li>Готово — говорите «вошёл», я забираю управление.</li>
</ol>
"""+spoiler("Почему через экран, а не «дай пароль»",
            """<p>Пароль, отданный в переписке, остаётся в истории чата навсегда. Через экран
он вводится прямо в браузер и в переписку не попадает.</p>
<p>Сессия живёт в браузере на моей машине — значит, второй раз входить не придётся,
пока вы сами не решите выйти.</p>""")))

sections.append(dict(
    id="s4", chip="Репозиторий", title="Шаг 2. Приватный репозиторий",
    html="""
<p class="thesis">Репозиторий создаю я сам — сразу после входа. Видим только вы и я.</p>
<p>Структура, чтобы вы могли зайти и посмотреть:</p>
<pre><code>memory/
├── styles/        стили отчётов, 01…0N + галерея index.html
├── projects/      по папке на проект, PROJECT.md внутри
├── dashboard/     index.md — всегда на виду
└── README.md</code></pre>
"""+spoiler("Что важно про приватность",
            """<p>Приватный репозиторий виден только владельцу и тем, кому вы дали доступ.
Токен, который вы выпустите, будет действовать на <b>один</b> этот репозиторий —
не на весь аккаунт.</p>""")))

sections.append(dict(
    id="s5", chip="Cloudflare", title="Шаг 3. Cloudflare Pages",
    html="""
<p class="thesis">Нужны два значения: токен API и Account ID. Оба — из панели Cloudflare.</p>
<ol class="steps">
<li>Войдите в Cloudflare (можно тем же способом — на экране).</li>
<li>My Profile → API Tokens → Create Token → Custom token.</li>
<li>Права: <b>Account → Cloudflare Pages → Edit</b>. Больше ничего.</li>
<li>Скопируйте токен — он показывается один раз.</li>
<li>Account ID — на странице Overview аккаунта, справа в блоке API.</li>
</ol>
"""+spoiler("Куда положить эти два значения",
            """<p>В репозитории: Settings → Secrets and variables → Actions →
New repository secret. Имена ровно такие:</p>
<pre><code>CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID</code></pre>
<p>Это можно сделать и без вас — если вы дали мне доступ. Но лучше вы: секреты
добавляются в интерфейсе за минуту и в переписку не попадают.</p>""", tip=True)))

sections.append(dict(
    id="s6", chip="Почта", title="Про почту с подтверждениями",
    html="""
<p class="thesis"><b>Пароль от Gmail я не возьму.</b> Не из вредности — из правила:
логины и пароли в чат я не принимаю и не храню.</p>
<p>Что работает вместо этого:</p>
<ul>
<li>коды подтверждения приходят вам — вы читаете их сами и вводите на экране;</li>
<li>если хотите, чтобы я разбирал письма — это отдельный ящик, подключённый штатно,
а не пароль от личного;</li>
<li>для GitHub и Cloudflare почта нужна только на этапе входа, дальше — токены.</li>
</ul>
"""+spoiler("Почему так, а не «просто дай доступ»",
            """<p>Ботовый Gmail — это ключ ко всему, что к нему привязано: восстановление паролей,
подтверждения входов, сброс доступа. Даже если доверяете — такой ключ не должен
проходить через переписку.</p>
<p>Практическая альтернатива: отдельный ящик для ботов, к которому доступ выдаётся
через штатное подключение, а не паролем в чате.</p>""", tip=True)))

sections.append(dict(
    id="s7", chip="Дальше", title="Что делаю я",
    html="""
<p class="thesis">После входа и токенов работа идёт без вас.</p>
<ul>
<li>создаю репозиторий и переношу стили (01, 02… + галерея);</li>
<li>пишу <code>.github/workflows/pages-deployment.yaml</code> для Cloudflare Pages;</li>
<li>проверяю сборку локально, потом пушу;</li>
<li>даю вам ссылку — открывается на iPhone из любого места.</li>
</ul>
"""+spoiler("Безопасность: как отозвать доступ",
            """<p>Токен GitHub — срок 7 дней, потом новый. Отозвать: Settings → Developer settings
→ Personal access tokens → Delete.</p>
<p>Токен Cloudflare — My Profile → API Tokens → Roll/Delete. Вход в браузере —
выйти из аккаунта на экране, и сессия умрёт.</p>
<p>Один репозиторий, одно право на запись — худшее, что может случиться: пропадёт
доступ к этому репозиторию. Не ко всему аккаунту.</p>""")))

doc = page(
    title="GitHub и Cloudflare Pages",
    kicker="ИИ-Консьерж · настройка",
    subtitle="Что нужно от вас, чтобы дальше всё шло без вашего участия.",
    sections=sections,
    footer="Версия 1 · 2026-11-25 · приватный репозиторий, токены узкие")

out = pathlib.Path("/workspace/home/Documents/github-cloudflare-guide.html")
out.write_text(doc, encoding="utf-8")
print("OK", len(doc), "bytes ->", out)
