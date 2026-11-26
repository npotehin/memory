<!--
ПРОИСХОЖДЕНИЕ: НАШЕ, НАПИСАНО С НУЛЯ
Автор: MultiTool для Никиты Потехина, 26.11.2026
Проверка происхождения скиллов из skills-src/. Источники — публичные репозитории
и побайтовое сравнение, а не пометки в шапках файлов.
-->
# Аудит происхождения скиллов

**Объект:** `npotehin/memory`, ветка `main`, HEAD `dbaceda` (26.11.2026), каталог `skills-src/` — 20 навыков, 166 файлов, 1 365 101 байт текста.
**Вопрос:** скиллы написаны разработчиком сервиса с нуля или взяты из открытых источников и адаптированы?
**Ответ коротко:** текст навыков — свой (похоже, собран по одному шаблону), но два навыка из двадцати содержат дословную копию чужого MIT-скилла, а девять внешних проектов используются как зависимости. Юридически это допустимо, оформление лицензий — нет.

---

## 1. Как проверялось

| Шаг | Что сделано |
|---|---|
| Выборка | Три навыка выбраны случайно из 20 (`shuf`): `video-audio`, `change-monitoring`, `source-research` |
| Поиск первоисточника | Все внешние ссылки из выбранных навыков; проверка репозиториев через GitHub API (лицензия, звёзды, дата) |
| Сверка текста | Побайтовое сравнение файлов навыка с файлами upstream на **закреплённой в тексте ревизии**, а не на HEAD |
| Поиск копий в целом | Дубликаты внутри каталога по md5; поиск по коду GitHub на характерные формулировки (русские и английские) |
| Чего не проверялось | Приватные каталоги сервисов, внутренние репозитории разработчика, авторство русских текстов по существу |

Критерий «дословная копия»: файл совпадает с источником посимвольно, отличия сводятся к служебной шапке и снятому заголовку H1.

---

## 2. `video-audio` — на две трети чужой MIT-скилл

Навык занимает 232 401 байт. Из них 153 820 байт (66,2%) — четыре файла, целиком взятые из [`kajisho5/ffmpeg-skill`](https://github.com/kajisho5/ffmpeg-skill).

Источник: MIT, 11 184 звезды, создан 03.09.2026, последний пуш 25.11.2026. Описание репозитория: «Local video editor for coding agents: 42 FFmpeg tools… for Claude Code, Cursor and Codex».

| Файл в навыке | Upstream | В навыке | Отличие |
|---|---|---|---|
| `references/ffmpeg/upstream-skill.md` | 29 995 б | 30 219 б | снята первая строка `---`, добавлена шапка на 224 б |
| `references/ffmpeg/scripts.md` | 100 528 б | 100 508 б | снят заголовок H1, один пустой перевод строки |
| `references/ffmpeg/gotchas.md` | 19 445 б | 19 394 б | снят заголовок H1 |
| `references/ffmpeg/devices.md` | 2 957 б | 2 901 б | снят заголовок H1 |

Сверка шла по ревизии `008333aaf6722083392eb6bd8bd67b59884a2a26` (версия 2.5.1), закреплённой в `references/ffmpeg.md:7` и в `SKILL.md:22`. Текущий HEAD upstream уже отличается — то есть копия снята с конкретного коммита и это корректно зафиксировано.

Что в навыке своё: русская обвязка `acquisition.md`, `downloads.md`, `production.md`, `story-motion.md`, `quality-delivery.md`, `media-editing.md`, `audio-captions.md`, `workflows.md` и сам `SKILL.md`, который маршрутизирует запросы между своей и чужой частями.

Ветка HyperFrames ссылается на [`heygen-com/hyperframes`](https://github.com/heygen-com/hyperframes) (Apache-2.0, 90 265 звёзд), но там только ссылки на официальную документацию и зафиксированная версия CLI 0.8.143 — текста upstream в навыке нет.

---

## 3. `change-monitoring` — текст свой, логика чужая

Дословных заимствований не найдено. Навык переписан своими словами, но опирается на три открытых проекта:

| Проект | Лицензия | Звёзды | Как используется |
|---|---|---|---|
| [`dgtlmoon/changedetection.io`](https://github.com/dgtlmoon/changedetection.io) | Apache-2.0 | 36 045 | ссылки на `changedetectionio/diff` и `changedetectionio/conditions` как образец сравнения и условий |
| [`D4Vinci/Scrapling`](https://github.com/D4Vinci/Scrapling) | BSD-3-Clause | 105 825 | повторяемое извлечение без модели, версия 0.4.15 |
| [`browser-use/browser-use`](https://github.com/browser-use/browser-use) | MIT | 122 093 | настройка адаптера извлечения |

Собственная часть: контракт наблюдения (объект, источник, поле, условие, частота), нормализованное наблюдение, baseline, состояния и события. Исполняемый helper `scripts/watch.py` в репозиторий не переносился — по правилам выгрузки скрипты остаются вне репозитория, поэтому проверить его код нельзя.

---

## 4. `source-research` — своё, на открытых библиотеках

Текст оригинальный. Внешние зависимости указаны с версиями и лицензиями:

| Библиотека | Версия | Лицензия | Звёзды | Роль |
|---|---|---|---|---|
| [`microsoft/markitdown`](https://github.com/microsoft/markitdown) | 0.1.8 | MIT | 198 505 | DOCX/PPTX/XLSX/HTML → Markdown |
| [`natasha/natasha`](https://github.com/natasha/natasha) | 1.6.0 | MIT | 1 364 | русская морфология, кандидаты фактов |
| [`no-plagiarism/pymorphy3`](https://github.com/no-plagiarism/pymorphy3) | — | MIT | 152 | морфология для Natasha |
| [`snowballstem/snowball`](https://github.com/snowballstem/snowball) | 3.1.1 | BSD-3-Clause | 897 | стеммер русского языка |

Собственная часть: дисковый корпус, SQLite-поиск, цитаты с locators, дедупликация версий по хешу, экспорт HTML-блокнота (`grounded.py`), а также отдельный сценарий чтения веб-страницы. [`PrimeIntellect-ai/prime-agent`](https://github.com/PrimeIntellect-ai/prime-agent) упомянут как необязательная опция, если уже установлен.

---

## 5. Каталог целиком: признаки одного шаблона

Следы ручной работы на 20 навыков не просматриваются — наоборот, каталог собран механически из общего каркаса:

| Наблюдение | Детали |
|---|---|
| Один общий файл в 17 навыках | `references/runtime-and-delivery.md`, md5 `fb0e9ab0017254e584889826c93d72c5`, 6 043 б — побайтово одинаков в 17 из 20 |
| Один общий файл в 6 навыках | `references/official-api.md` (PubMed, wger, Open Food Facts, HH, ЦБ, MOEX, Mealie, Firefly III, NHTSA) вставлен без изменений в `career-assistant`, `fitness-progress`, `food-planning`, `health-navigator`, `personal-finance`, `tech-support` |
| Один блок в двух навыках | ffmpeg-часть (154 КБ) целиком лежит и в `video-audio`, и в `media-processing`; ещё 7 справочников у них совпадают побайтово |
| Общий стиль | сжатые императивные формулировки, одинаковые связки («прочитай ветку перед её этапом», «не объявляй…»), внутренние термины платформы: `skills prepare`, coder, gateway, native cron, sandbox |

В `media-processing` чужой ffmpeg-блок занимает 153 820 из 177 342 байт — 86,7%.

Публичного «пакета скиллов», откуда скопирован русский текст, найти не удалось: поиск по коду GitHub не находит ни русских, ни английских совпадений. Вероятнее всего, тексты написаны внутри сервиса — в том числе машинно — по единому шаблону.

---

## 6. Ещё одна адаптация, о которой сказано честно

`mobile-reports/references/design.md` прямо сообщает: «Adapted from Anthropic's Apache-2.0 frontend-design skill. Modified for MultiTool's standalone HTML workflow». Сверка с [`anthropics/skills` → `skills/frontend-design`](https://github.com/anthropics/skills): совпадает 9 строк из 71 (12%) — это действительно переработка, а не копия, с корректной атрибуцией и указанием лицензии. Так и надо.

---

## 7. Лицензии: что разрешено и что не выполнено

Разрешено: MIT, Apache-2.0 и BSD-3-Clause допускают коммерческое использование, переработку и распространение.

Не выполнено:

1. **Нет ни одного файла лицензии.** В репозитории отсутствует `LICENSE.upstream`, хотя `skills-src/video-audio/SKILL.md:9` и `references/ffmpeg.md:7` утверждают, что «авторство и MIT-лицензия сохранены в `LICENSE.upstream`». `skills-src/PROGRESS.md` объясняет: «LICENSE.upstream в репозиторий не переносятся (правило: SKILL.md и справочники)». MIT требует включать текст лицензии и уведомление о копирайте в каждую копию — сейчас это не так.
2. **Неверная шапка происхождения.** `references/ffmpeg/upstream-skill.md` помечен «ПРОИСХОЖДЕНИЕ: ОРИГИНАЛ РАЗРАБОТЧИКА, НЕ ИЗМЕНЁН», хотя текст принадлежит kajisho5. Та же шапка стоит на `mobile-reports/references/design.md`, который сам же признаёт себя адаптацией Anthropic.
3. **Одна и та же чужая часть дважды.** ffmpeg-блок продублирован в `video-audio` и `media-processing` — при обновлении upstream придётся править два места.

Что сделано правильно: указан автор, лицензия и закреплённая ревизия; текст не выдан за свой; адаптация Anthropic подписана.

---

## 8. Вывод

Гипотеза «взяли популярное open-source и положили к себе» верна частично.

- Как **скиллы** чужое взято только дважды: `kajisho5/ffmpeg-skill` (MIT) внутри `video-audio` и `media-processing`.
- Как **инструменты** открытый код используется широко: changedetection.io, Scrapling, browser-use, markitdown, Natasha, snowballstemmer, HyperFrames, yt-dlp.
- Русские тексты 18 навыков из 20 — собственные, но сделаны по единому шаблону: 17 одинаковых `runtime-and-delivery.md`, 6 одинаковых `official-api.md`, общий стиль и общая терминология платформы.

Риск не в копировании, а в оформлении: лицензия MIT заявлена, но не приложена, а шапки происхождения врут на четырёх файлах.

---

## 9. Что поправить

1. Положить `LICENSE.upstream` (текст MIT + copyright kajisho5) в `video-audio/references/ffmpeg/` и `media-processing/references/ffmpeg/`; либо убрать из текста утверждение, что лицензия сохранена.
2. Заменить шапку на `ПРОИСХОЖДЕНИЕ: ОРИГИНАЛ kajisho5/ffmpeg-skill, MIT, ревизия 008333a…` в четырёх файлах и на `АДАПТАЦИЯ Anthropic frontend-design, Apache-2.0` в `design.md`.
3. Хранить ffmpeg-блок в одном месте и ссылаться на него из второго навыка, чтобы не расходились версии.
4. В `PROGRESS.md` исправить правило «лицензии не переносятся» — оно противоречит MIT и собственному тексту навыка.

---

## 10. Как воспроизвести

```sh
git clone https://github.com/npotehin/memory.git && cd memory

# лицензия и метаданные источника
gh api repos/kajisho5/ffmpeg-skill \
  --jq '{license:.license.spdx_id, stars:.stargazers_count, pushed_at}'

# текст upstream на закреплённой ревизии
gh api "repos/kajisho5/ffmpeg-skill/contents/references/gotchas.md?ref=008333aaf6722083392eb6bd8bd67b59884a2a26" \
  --jq '.content' | base64 -d > /tmp/gotchas-up.md
sed '1,5d' skills-src/video-audio/references/ffmpeg/gotchas.md > /tmp/gotchas-loc.md
diff /tmp/gotchas-up.md /tmp/gotchas-loc.md

# дубликаты внутри каталога
find skills-src -name '*.md' -exec md5sum {} + | sort | uniq -c -w32 | sort -rn | head
```
