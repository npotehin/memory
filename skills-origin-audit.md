<!--
ПРОИСХОЖДЕНИЕ: НАШЕ, НАПИСАНО С НУЛЯ
Автор: MultiTool для Никиты Потехина, 26.11.2026
Проверка происхождения всех 20 скиллов из skills-src/. Источники — публичные
репозитории и побайтовое сравнение, а не пометки в шапках файлов.
-->
# Аудит происхождения скиллов

**Объект:** `npotehin/memory`, ветка `main`, каталог `skills-src/` — 20 навыков, 166 файлов, 1 365 101 байт текста.
**Вопрос:** скиллы написаны разработчиком сервиса с нуля или взяты из открытых источников и адаптированы?
**Ответ коротко:** проверены все 20. Дословная копия чужого текста — в двух навыках (`video-audio`, `media-processing`), это один и тот же MIT-блок FFmpeg. Одна честно подписанная адаптация — `mobile-reports/references/design.md` (Anthropic, Apache-2.0). Остальные 17 написаны свои́ми словами, но опираются на открытые библиотеки и API. Проблема не в копировании, а в оформлении: файла лицензии нет, а шапки происхождения на пяти файлах неверны.

---

## 1. Как проверялось

| Шаг | Что сделано |
|---|---|
| Полнота | Проверены все 20 навыков, а не выборка. Работа шла четырьмя группами параллельно, у каждой — один и тот же протокол |
| Ссылки | Из каждого навыка извлечены все внешние URL, каждой назначена роль: документация, библиотека-зависимость, источник скопированного текста, пример-заглушка |
| Метаданные | Для каждого GitHub-репозитория через API получены лицензия, число звёзд, дата последнего пуша |
| Сверка текста | Файлы навыков сравнивались с upstream **на закреплённой в тексте ревизии**, а не на HEAD. Отличия в виде снятого заголовка H1 и добавленной шапки (~220 б) считались дословной копией |
| Поиск копий | Дубликаты внутри каталога по md5; поиск по коду GitHub на характерные русские и английские формулировки |
| Перепроверка | Ключевые заявления агентов (лицензии, звёзды, доли, совпадения) проверены заново вручную; одно завышение доли исправлено |
| Чего не проверялось | Приватные каталоги сервисов, внутренние репозитории разработчика; код скриптов, которых нет в выгрузке |

Критерии вердикта:

- **своё** — внешних источников текста нет;
- **своё + OSS** — текст свой, снаружи библиотеки, API или инструменты;
- **адаптация** — чужая идея и структура, переписанные словами, с указанием источника;
- **дословная копия** — файл совпадает с источником посимвольно, кроме служебной шапки и снятого H1.

---

## 2. Итоговая таблица: 20 из 20

| # | Навык | Объём | Вердикт | Ключевое доказательство |
|---|---|---|---|---|
| 1 | `video-audio` | 232 401 б | **дословная копия 66,2%** | 4 файла из `kajisho5/ffmpeg-skill`, MIT, ревизия `008333a…` |
| 2 | `media-processing` | 177 342 б | **дословная копия 86,7%** | тот же блок; в справочниках 153 820 из 172 783 б |
| 3 | `mobile-reports` | 157 466 б | своё + OSS, `design.md` — адаптация | Anthropic `frontend-design`, Apache-2.0; 0 из 25 предложений близки более чем на 0,8 |
| 4 | `career-assistant` | 97 985 б | своё + OSS | только документация HH API; чужих MCP нет |
| 5 | `personal-finance` | 83 312 б | своё + OSS | actual (MIT), firefly-iii docs (AGPL-3.0) |
| 6 | `health-navigator` | 68 431 б | своё | NHS, МЧС, Минздрав — как опоры, без копирования |
| 7 | `video-production` | 65 240 б | своё + OSS | HyperFrames (Apache-2.0) как инструмент; текст свой |
| 8 | `fitness-progress` | 60 419 б | своё + OSS | wger (AGPL-3.0) через API; 0 совпавших строк с его доками |
| 9 | `tech-support` | 58 840 б | своё + OSS | mobile-mcp (Apache-2.0, ★10 891), ifixit-mcp (0BSD) — инструменты |
| 10 | `travel-leisure` | 52 307 б | своё + OSS | только официальная документация 2GIS, Google, Yandex |
| 11 | `source-research` | 51 862 б | своё + OSS | markitdown (MIT, 0.1.8), Natasha (MIT), snowball (BSD-3) |
| 12 | `food-planning` | 41 866 б | своё + OSS | recipe-scrapers (MIT, pinned `e7892149`); 0 общих строк |
| 13 | `news-briefing` | 40 586 б | своё | feedparser (MIT) как зависимость; `krche` — внутреннее имя |
| 14 | `presentations` | 37 074 б | своё | собственный OpenSlide-сценарий, MDN как справка |
| 15 | `change-monitoring` | 36 427 б | своё + OSS | changedetection.io (Apache-2.0), Scrapling (BSD-3), browser-use (MIT) |
| 16 | `documents` | 32 995 б | своё + OSS | markitdown (MIT), pypdf, PyMuPDF, python-docx |
| 17 | `learning-support` | 27 884 б | своё | внешних ссылок ноль |
| 18 | `shopping-research` | 24 946 б | своё + OSS | документация Shopify; сторонний MCP отклонён |
| 19 | `spreadsheets` | 6 554 б | своё, выгрузка неполная | один файл, три ссылки в никуда |
| 20 | `data-analysis` | 4 880 б | своё, выгрузка неполная | один файл, семь ссылок в никуда |

Итого: **2 навыка с дословной копией (10% по числу навыков, 22,5% по объёму каталога), 1 адаптация, 17 своих текстов.** Уникального чужого текста 153 820 б (11,3% каталога), в файлах его 307 640 б — блок положен дважды.

---

## 3. Дословные копии: `video-audio` и `media-processing`

Источник — [`kajisho5/ffmpeg-skill`](https://github.com/kajisho5/ffmpeg-skill): MIT, ★11 188, создан 03.09.2026, «42 FFmpeg tools… for Claude Code, Cursor and Codex». Ревизия `008333aaf6722083392eb6bd8bd67b59884a2a26` (версия 2.5.1) закреплена в тексте — это корректно.

| Файл в навыке | Upstream | В навыке | Отличие |
|---|---|---|---|
| `references/ffmpeg/upstream-skill.md` | 29 995 б | 30 219 б | снята первая `---`, добавлена шапка |
| `references/ffmpeg/scripts.md` | 100 528 б | 100 508 б | снят заголовок H1, один пустой перевод строки |
| `references/ffmpeg/gotchas.md` | 19 445 б | 19 394 б | снят заголовок H1 |
| `references/ffmpeg/devices.md` | 2 957 б | 2 901 б | снят заголовок H1 |

Доли: у `video-audio` блок занимает 153 820 из 232 401 б (66,2%), у `media-processing` — 153 820 из 177 342 б (86,7%), в справочниках второго — 89,0%. Семь справочников у этих двух навыков совпадают побайтово, `ffmpeg.md` тоже.

Своё в `video-audio`: `acquisition.md`, `downloads.md`, `production.md`, `story-motion.md`, `quality-delivery.md`, `media-editing.md`, `audio-captions.md`, `workflows.md` и `SKILL.md`. Своё в `media-processing`: `acquisition.md`, `downloads.md` и русские обёртки.

Ветка HyperFrames ссылается на [`heygen-com/hyperframes`](https://github.com/heygen-com/hyperframes) (Apache-2.0, ★90 265), но переносит только ссылки на документацию и версию CLI 0.8.143 — текста upstream нет.

---

## 4. Адаптация, сделанная правильно: `mobile-reports`

`references/design.md` (3 093 б) сообщает о себе прямо: «Adapted from Anthropic's Apache-2.0 frontend-design skill. Modified for MultiTool's standalone HTML workflow». Сверка с [`anthropics/skills` → `skills/frontend-design`](https://github.com/anthropics/skills):

- предложений в адаптации — 25, в оригинале — 69;
- ни одно предложение не достигает близости 0,8 (медиана 0,43, максимум 0,64);
- совпадают только общие термины дизайнерского лексикона.

Это переработка, а не копия, с корректной атрибуцией и указанием лицензии. Так и надо. Единственная претензия — шапка «ОРИГИНАЛ РАЗРАБОТЧИКА, НЕ ИЗМЕНЁН» на этом же файле противоречит его содержимому.

---

## 5. Чужие инструменты: что и под какой лицензией

| Проект | Лицензия | Звёзды | Роль |
|---|---|---|---|
| [`kajisho5/ffmpeg-skill`](https://github.com/kajisho5/ffmpeg-skill) | MIT | 11 188 | **скопированный текст** (2 навыка) |
| [`anthropics/skills`](https://github.com/anthropics/skills) → frontend-design | Apache-2.0 | 200 620 | **адаптированный текст** (1 файл) |
| [`heygen-com/hyperframes`](https://github.com/heygen-com/hyperframes) | Apache-2.0 | 90 265 | инструмент, инструкции |
| [`browser-use/browser-use`](https://github.com/browser-use/browser-use) | MIT | 122 093 | инструмент |
| [`D4Vinci/Scrapling`](https://github.com/D4Vinci/Scrapling) | BSD-3-Clause | 105 825 | библиотека |
| [`microsoft/markitdown`](https://github.com/microsoft/markitdown) | MIT | 198 505 | библиотека 0.1.8 |
| [`yt-dlp/yt-dlp`](https://github.com/yt-dlp/yt-dlp) | Unlicense | 210 781 | утилита |
| [`dgtlmoon/changedetection.io`](https://github.com/dgtlmoon/changedetection.io) | Apache-2.0 | 36 045 | образец логики |
| [`actualbudget/actual`](https://github.com/actualbudget/actual) | MIT | 30 462 | идеи/API бюджета |
| [`wger-project/wger`](https://github.com/wger-project/wger) | AGPL-3.0 | 7 326 | API тренировок |
| [`mobile-next/mobile-mcp`](https://github.com/mobile-next/mobile-mcp) | Apache-2.0 | 10 891 | инструмент |
| [`hhursev/recipe-scrapers`](https://github.com/hhursev/recipe-scrapers) | MIT | 2 267 | библиотека, pinned |
| [`natasha/natasha`](https://github.com/natasha/natasha) | MIT | 1 364 | библиотека |
| [`snowballstem/snowball`](https://github.com/snowballstem/snowball) | BSD-3-Clause | 897 | стеммер |
| [`no-plagiarism/pymorphy3`](https://github.com/no-plagiarism/pymorphy3) | MIT | 152 | морфология |
| [`Dthen/ifixit-mcp`](https://github.com/Dthen/ifixit-mcp) | 0BSD | 1 | инструмент |
| [`firefly-iii/api-docs`](https://github.com/firefly-iii/api-docs) | AGPL-3.0 | 9 | документация API |

Отдельно: Open Food Facts — данные под ODbL (в навыке это отмечено верно); parse5, acorn, postcss, jszip — MIT (заявлено в `mobile-reports/scripts/archive/README.md`).

Про AGPL: `wger` и `firefly-iii` используются через HTTP API, код не распространяется. Но если когда-нибудь код этих проектов попадёт в поставку, AGPL потребует раскрытия — это стоит держать в голове.

---

## 6. Своё без внешних зависимостей

`learning-support` (27 884 б) — ни одной внешней ссылки: страницы пересылаются смежным навыкам. `health-navigator` (68 431 б) — ссылки на NHS, МЧС, Минздрав, Cochrane как опоры, но текст собственный. `news-briefing` (40 586 б) — только документация Python и feedparser; `krche` не найден ни на GitHub, ни в поиске кода, инструменты `news_feed`, `news_sources`, `news_interests` описаны как будущие — это внутреннее имя сервиса, а не внешний продукт. `presentations` (37 074 б) — собственный сценарий OpenSlide и разбор реального кейса; с Anthropic `pptx` совпадений нет. `data-analysis` и `spreadsheets` — по одному файлу, проверять на копирование нечего.

---

## 7. Каталог собран по шаблону

| Наблюдение | Детали |
|---|---|
| Один общий каркас | `references/runtime-and-delivery.md`, 6 043 б, md5 `fb0e9ab0…` — побайтово в 17 навыках |
| Один общий справочник | `references/official-api.md`, 7 870 б, md5 `1d8db082…` — в 6 навыках: career-assistant, fitness-progress, food-planning, health-navigator, personal-finance, tech-support |
| Один блок в двух навыках | ffmpeg-часть (154 КБ) в `video-audio` и `media-processing`; ещё 7 файлов совпадают |
| Общий стиль | сжатые императивные формулировки, одинаковые связки, внутренние термины платформы: `skills prepare`, coder, gateway, sandbox, native cron, `hera-app`, `apps build`, Hermes |

Общий `official-api.md` покрывает 10 источников (PubMed, Europe PMC, wger, Open Food Facts, HH, ЦБ, MOEX, Mealie, Firefly III, NHTSA) — и вставлен всем шести навыкам без отбора: у финансов в нём лишние медицинские источники, а в `tech-support` файл лежит, но не подключён. Это механическая сборка, а не проработанный под каждый навык справочник.

Публичного пакета, откуда скопирован русский текст, нет: поиск по коду GitHub не даёт совпадений ни на русском, ни на английском.

---

## 8. Неполная выгрузка: чего не хватает

| Навык | Чего нет |
|---|---|
| `spreadsheets` | единственный `SKILL.md`; отсутствуют `formulas-and-design.md`, `csv.md`, `headless-runtime.md`, `assets/workbook-spec.json` |
| `data-analysis` | единственный `SKILL.md`; отсутствуют 7 справочников и `assets/dashboard-spec.json` |
| `career-assistant` | `assets/resume.html`, `assets/career-record.schema.json` |
| `health-navigator` | `scripts/health_records.py` |
| `personal-finance` | `scripts/receipts.py` |
| 6 навыков | `scripts/official_sources.py`, `tests/test_official_sources.py` |
| `mobile-reports` | `vendor/parsers.cjs` (640 КБ) — без него `site.cjs` не запускается, хотя в `PROGRESS.md` описано, что рабочая конфигурация возвращена |

Отдельно: в `mobile-reports/origin/site.cjs` стоит пометка «есть наши правки», но вне шапок файл расходится с `scripts/site.cjs` на 0 строк — правок нет.

---

## 9. Лицензии: что разрешено и что не выполнено

Разрешено: MIT, Apache-2.0, BSD-3-Clause и 0BSD допускают коммерческое использование, переработку и распространение.

Не выполнено:

1. **Нет файла лицензии.** `LICENSE.upstream` объявлен в `skills-src/video-audio/SKILL.md:9` и `references/ffmpeg.md:7`, но в репозитории отсутствует. `PROGRESS.md` объясняет: «лицензии в репозиторий не переносятся». MIT требует включать текст лицензии и уведомление о копирайте в каждую копию.
2. **Неверные шапки происхождения — 5 файлов.** Четыре файла ffmpeg-блока и `mobile-reports/references/design.md` помечены «ОРИГИНАЛ РАЗРАБОТЧИКА, НЕ ИЗМЕНЁН», хотя первые принадлежат kajisho5, а последний сам признаёт адаптацию Anthropic.
3. **Один блок хранится дважды.** При обновлении upstream править придётся два навыка, версии разойдутся.
4. **Нет текста Apache-2.0 рядом с адаптацией.** `LICENSE.txt` Anthropic в репозиторий не перенесён.

Что сделано правильно: автор, лицензия и закреплённая ревизия указаны; чужой текст не выдан за свой; адаптация Anthropic подписана; лицензии данных (ODbL у Open Food Facts, отдельная лицензия данных iFixit) отмечены.

---

## 10. Вывод

Гипотеза «взяли популярное open-source и положили к себе» подтверждается частично.

- Как **скиллы** чужое взято дважды, и это один и тот же MIT-блок FFmpeg: `kajisho5/ffmpeg-skill` внутри `video-audio` и `media-processing`. Плюс одна переработка Anthropic в `mobile-reports`.
- Как **инструменты** открытый код используется почти везде: changedetection.io, Scrapling, browser-use, markitdown, Natasha, snowballstemmer, HyperFrames, yt-dlp, recipe-scrapers, actual, feedparser, MCP-серверы для телефонов и iFixit.
- Русские тексты 17 навыков из 20 — собственные, но сделаны по единому шаблону: 17 одинаковых `runtime-and-delivery.md`, 6 одинаковых `official-api.md`, общая терминология платформы.

Риск не в копировании, а в оформлении и в полноте: MIT-лицензия заявлена, но не приложена; шапки врут на пяти файлах; два навыка выгружены без справочников и неработоспособны как пакеты.

---

## 11. Что поправить

1. Положить `LICENSE.upstream` (текст MIT + copyright kajisho5) рядом с ffmpeg-справочниками и `LICENSE.txt` Anthropic рядом с `mobile-reports/references/design.md`; либо убрать из текста утверждение, что лицензия сохранена.
2. Исправить шапки: «оригинал kajisho5/ffmpeg-skill, MIT, ревизия 008333a…» — на четырёх файлах; «адаптация Anthropic frontend-design, Apache-2.0» — на `design.md`.
3. Хранить ffmpeg-блок в одном месте и ссылаться на него из второго навыка.
4. Дособрать выгрузки `spreadsheets` и `data-analysis`: сейчас у них нет ни одного справочника из тех, на которые ссылается `SKILL.md`.
5. Убрать из `PROGRESS.md` правило «лицензии не переносятся» — оно противоречит MIT и тексту самих навыков.

---

## 12. Как воспроизвести

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

# доля чужого блока
du -sb skills-src/media-processing
du -cb skills-src/media-processing/references/ffmpeg/*.md | tail -1
```

Как шёл аудит: 20 навыков разделены на четыре группы, каждая проверена отдельным агентом по одному протоколу (ссылки → метаданные лицензий → сверка с upstream по закреплённой ревизии → проверка шапок и дубликатов). Заявления о копировании и доли пересчитаны вручную; одно завышение (`media-processing` — «99% справочников») исправлено на 89,0%.
