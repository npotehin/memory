<!--
ПРОИСХОЖДЕНИЕ: ОРИГИНАЛ РАЗРАБОТЧИКА, НЕ ИЗМЕНЁН
Получено чтением из каталога скиллов сервиса, записано байт в байт.
-->
# Извлечение и существующий браузер

Сначала выясни, откуда получить проверяемое значение: официальный API/JSON,
RSS/Atom, структурированные данные HTML, затем нужный DOM-участок.
Не скачивай весь сайт и не сравнивай полную страницу, если нужно одно поле.
Pagination должна завершиться в выбранном scope; неполный ответ не становится
полным пустым списком. Наличие cache отмечай; stale значение не выдавай за текущую цену.

## Scrapling

Просмотренный upstream pyproject задаёт 0.4.15, Python >=3.10. Перед установкой
проверь наличие этой закреплённой версии и совместимость с Python sandbox;
если её нет, выбери доступный pin после чтения release notes и проверки API.
Базовый parser можно установить project-local:

```sh
uv venv .venv
uv pip install --python .venv/bin/python 'scrapling==0.4.15'
```

Переиспользуй уже созданный venv, не перезаписывай его. Это инструкции первой
установки, не утверждение о наличии Scrapling. Не устанавливай all/ai/shell или
ещё один Chromium ради CSS-парсинга. Готовый HTML можно разобрать через
`from scrapling.parser import Selector; page = Selector(html, url=source_url)`;
проверяй актуальную API закреплённой версии. Для HTTP fetchers нужны дополнительные
зависимости, выбирай их только если прямого штатного HTTP/браузера недостаточно.

Для динамической страницы Scrapling поддерживает cdp_url/executable_path, но
это не доказывает разрешённый CDP-доступ из нашего cron. Сначала проверь реальный
контракт broker lifecycle/lease. По возможности бери HTML из существующей
разрешённой браузерной операции и используй parser отдельно. Не открывай порт
браузера наружу, не извлекай служебный endpoint/токен из процессов и не закрывай
browser-use context. Если unattended browser path отсутствует, не обещай такую
проверку по расписанию; HTTP/доступный API — самостоятельный fallback.

Настрой adapter через browser-use/coder: получить страницу, выбрать конкретное
поле, сверить идентичность, сформировать нормализованное observation и выполнить
с helper. Повторная простая проверка не вызывает browser-use LLM каждый раз.
Для источника, требующего входа, используй только разрешённую пользовательскую
сессию и нативные правила unattended; ручной login не гарантирует доступ cron.

Adaptive selector сохраняет признаки элемента в SQLite. Назначь storage внутри
каталога конкретного наблюдения. При перестройке DOM похожий элемент — кандидат,
не доказательство: сверяй SKU/название/вариант/тип цены и единицу. Несколько подходящих
элементов или неуверенное соответствие — check_failed, baseline не обновляется.
Автосохранение ошибочного кандидата не должно закреплять неверный селектор.

Документация: [Scrapling](https://github.com/D4Vinci/Scrapling),
[зависимости](https://github.com/D4Vinci/Scrapling/blob/main/pyproject.toml),
[CDP](https://scrapling.readthedocs.io/en/latest/fetching/dynamic.html),
[adaptive](https://scrapling.readthedocs.io/en/latest/parsing/adaptive.html).

## changedetection.io

Оттуда переиспользован подход: выбранный участок, нормализация, снимок → изменение,
условие уведомления. В helper upstream-код не скопирован. Их diff использует
difflib/diff-match-patch; простое typed сравнение не требует переноса UI-рендерера.
Функции условий связаны с Flask/plugins, весь runtime и собственный scheduler
нам не нужны. Если позже переносится конкретный код, закрепи ревизию, сохрани
Apache-2.0/атрибуцию/NOTICE при наличии, отметь изменения и проверь функции/зависимости.
Scrapling лицензирован BSD-3-Clause; сохраняй уведомления при распространении.

Ссылки: [diff](https://github.com/dgtlmoon/changedetection.io/tree/master/changedetectionio/diff),
[условия](https://github.com/dgtlmoon/changedetection.io/tree/master/changedetectionio/conditions),
[лицензия](https://github.com/dgtlmoon/changedetection.io/blob/master/LICENSE).
MCP для выбранной архитектуры не нужен: нативные инструменты уже дают настройку,
запуск, статус и доставку. Community changedetection MCP требует running server
и не заменяет получение данных или историю нашего наблюдения.
