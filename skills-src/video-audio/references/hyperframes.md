<!--
ПРОИСХОЖДЕНИЕ: ОРИГИНАЛ РАЗРАБОТЧИКА, НЕ ИЗМЕНЁН
Получено чтением из каталога скиллов сервиса, записано байт в байт.
-->
# HyperFrames: локальный детерминированный рендер

Официальные инструкции: [quickstart](https://hyperframes.heygen.com/quickstart), [репозиторий и skills](https://github.com/heygen-com/hyperframes). Уточняй контракт по установленной версии и её `--help`; примеры ниже не подменяют актуальное API. На 2026-10-09 smoke использует CLI 0.8.143.

## Первое использование

Проверь Node, ffmpeg/ffprobe и существующий Chromium. Для своего небольшого проекта установи HyperFrames project-local, сохрани точную версию и package-lock. GSAP при использовании также сохраняй локально: CDN не нужен во время capture. Штатный `init` подходит новому проекту; его параметры смотри в `init --help`.

Если уже доступны официальные skills, используй нужный workflow и domain references; не копируй весь их toolkit в каждый ролик. В изолированном CI/test допускается `HYPERFRAMES_SKIP_SKILLS=1`, чтобы setup не изменял глобальный каталог skills. Этот режим не заменяет чтение авторского контракта.

Переиспользуй установленный браузер через поддерживаемый `HYPERFRAMES_BROWSER_PATH`. Не скачивай второй Chromium без необходимости. Новая установка, инициализация проекта и существующий рабочий lockfile — разные операции; рабочий проект не надо самовольно обновлять.

## Композиция

Standalone `index.html` имеет root непосредственно в body, без template: `data-composition-id`, `data-width`, `data-height`, явный `data-duration`, при необходимости `data-fps`. Root занимает 100% размера; canvas задают attributes. Timed clips имеют start/duration. Для модульных сцен проверь текущий контракт sub-compositions: шаблон и script/style должны оказаться в собираемой области, IDs и timeline keys согласованы.

У sub-composition style/script находятся внутри `<template>`. Host и внутренний root имеют одинаковый `data-composition-id`, ему соответствует timeline key; DOM IDs остаются уникальными. Root сцены оформляй через ID, обычно `position:absolute; inset:0`. Относительная высота на неверном контейнере может оставить пустую полосу в MP4 даже при зелёном validator. Ассеты sub-composition в проверенной версии задаются относительно корня проекта (`assets/...`), без `../`. Не добавляй child timeline в master вручную: runtime уже делает локальный seek.

Пропорциональный root требует корректной высоты цепочки `html, body` и контейнера. Однако обрезка может быть дефектом capture, а не CSS: в smoke 0.8.143 с системным Chrome на macOS snapshot показывал полный кадр, прямой MP4 обрезал низ; изменение геометрии, software GPU и `--no-page-side-compositing` не помогли. Проверенный обход для этой среды — `render --format webm --output intermediate.webm`, затем ffmpeg в H.264/AAC MP4. Это условный fallback после воспроизведения, не обязательное двойное кодирование каждого ролика. Оpaque-композиция не требует прозрачности: предупреждение об alpha=255 в таком WebM само по себе не дефект. Проверяй конечный MP4 заново; не считай snapshot доказательством правильного экспорта.

GSAP: ровно одна завершённая paused timeline на композицию, зарегистрированная как `window.__timelines[compositionId]`. Сначала дождись локальных шрифтов/изображений и построения timeline; потом зарегистрируй. Не управляй проигрыванием wall clock. Framework управляет видимостью timed clips: не tween display/visibility/autoAlpha на clip-root; анимируй внутренний элемент. Не совмещай layout transform и движение на одном node.

Границы сцен имеют явные время и финальное состояние. Конец root не должен отрезать нужный clip или звук. Вложенный video не должен одновременно иметь timing поверх timing обычного родителя, если это запрещает текущая версия. Media playback и seek принадлежат runtime; HTML autoplay не задаёт правильный кадр рендера.

Для audio укажи id, локальный src, start/duration и track; сохранение исходного звука у video и отдельная музыка/речь — разные дорожки. Проверяй фактический результат mixer в MP4. Наличие volume в source не подтверждает слышимость экспортированной дорожки.

## Команды и проверка

При project-local установке доступны `npx hyperframes` или npm scripts. Пример цикла:

```sh
npx hyperframes lint
npx hyperframes timeline --json
npx hyperframes check --at 0.5,2,4,6 --at-transitions --json
npx hyperframes snapshot --at 2,6
npx hyperframes render --output final.mp4
```

Значения времени выбирай по реальному storyboard. Уточняй snapshot/output flags через help. `check` сам запускает lint: отдельный lint нужен для ранних правок, не как дублирующий финальный gate. Ошибка lint может выключить layout/contrast sampling; проверка с нулём samples не считается выполненной.

Сначала небольшой тестовый экспорт перехода и медиа, затем полный файл. Настрой workers/качество под ресурсы и измеренный пробный рендер; не принимай auto-calibration за гарантию отсутствия перегрузки. GUI не требуется. Preview Studio полезен при запрошенном ревью, но локальный URL не является доставленным MP4.

Проверь итоговый файл и сохранённые кадры согласно `quality-delivery.md`. Зафиксируй версию, команду, среду, длительность и ограничения в проекте. Установка CLI не даёт сама по себе API голоса, avatars, generative video или платного cloud rendering: медиа создаются доступными штатными инструментами.

## Интеграция

У Muse уже есть coder, browser и sender. CLI вызывается через них; отдельный MCP/сервис для этого цикла не требуется. Установка в sandbox при первом вызове не означает, что сервер подключён к tool catalog. Не передавай пользовательские исходники и отчёты во внешние feedback/publish сервисы без поручения пользователя.
