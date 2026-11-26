# Прогресс выгрузки скиллов

Исходники: `skills-src/<slug>/`. Выкладываются SKILL.md и справочники. Скрипты и тесты
в репозиторий не переносятся. По одному скиллу — один коммит.

## Выложены ранее
- mobile-reports — выложен
- spreadsheets — выложен
- data-analysis — выложен

## Батч A
- personal-apps — пропущен: скилл с таким именем не найден в каталоге публикации
- presentations — выложен (6 файлов: SKILL.md + 5 справочников)
- documents — выложен (8 файлов: SKILL.md + 6 справочников + assets/document-style.json)

## Батч B
- source-research — выложен (9 файлов: SKILL.md + 8 справочников; scripts/ и tests/ не переносились)
- news-briefing — выложен (6 файлов: SKILL.md + 5 справочников)
- shopping-research — выложен (4 файла: SKILL.md + 3 справочника)

## Батч C
- change-monitoring — выложен (5 файлов: SKILL.md + 4 справочника)
- tech-support — выложен (9 файлов: SKILL.md + 8 справочников)
- travel-leisure — выложен (6 файлов: SKILL.md + 5 справочников)

## Батч D
- career-assistant — выложен (11 файлов: SKILL.md + 10 справочников)
- learning-support — выложен (5 файлов: SKILL.md + 4 справочника)
- personal-finance — выложен (9 файлов: SKILL.md + 8 справочников)

## Батч E
- health-navigator — выложен (9 файлов: SKILL.md + 8 справочников)
- fitness-progress — выложен (8 файлов: SKILL.md + 7 справочников)
- food-planning — выложен (6 файлов: SKILL.md + 5 справочников)

## Батч F
- media-processing — выложен (9 файлов: SKILL.md + 4 справочника + references/ffmpeg/ 4 файла)
- video-audio — выложен (17 файлов: SKILL.md + 11 справочников + references/ffmpeg/ 4 файла + assets/storyboard.json)
- video-production — выложен (10 файлов: SKILL.md + 8 справочников + assets/storyboard.json)

## Итог
19 скиллов выложено, 1 пропущен (personal-apps). skills.html, папка skills/ и
build_skills.py не изменялись.

## Добор: код и тесты mobile-reports

- scripts/site.cjs — 25 КБ, 602 строки. Собран по частям из прочитанного текста, синтаксис проверен (node --check). Запуск без vendor/parsers.cjs невозможен — падает на загрузке модуля, это ожидаемо.
- scripts/build_mindmap.cjs — 21 КБ, 525 строк. Работает: собран HTML из JSON, заголовок «РКШ — интеллект-карта», 11 699 байт.
- scripts/templates/html/index.html — 1 137 байт.
- scripts/templates/react/ — 5 файлов (index.html, src/main.js, src/style.css, package.json, vite.config.js).
- tests/test_websites.py — 3 теста, 1 839 байт.
- vendor/parsers.cjs — НЕ выгружен: 640 730 символов, чтение обрезается. Сторонние парсеры HTML/JS/CSS/ZIP.
