# Источники, MCP и первый вызов

## Выбор источника

Сначала native web/search/extract/vision и официальная поддержка производителя.
Запрос включает модель, ревизию/версию, регион и симптом/код. Открой подходящую
статью/раздел PDF; для большого мануала используй source-research с цитатами страниц.
Сопоставь инструкцию с фактическим экраном и устройством. Community-ответ полезен
как гипотеза, а не доказательство диагноза или разрешение на firmware.

Опорные источники: [Microsoft Support](https://support.microsoft.com/),
[Apple Support](https://support.apple.com/), [Samsung](https://www.samsung.com/ru/support/),
[Bosch по E-Nr](https://www.bosch-home.com/us/owner-support/owner-manuals),
[Siemens](https://www.siemens-home.bsh-group.com/ie/customer-service/support/user-manuals/my-products),
[Keenetic model documentation](https://support.keenetic.ru/eaeu/sprinter/kn-3710/ru/index-ru.html),
[Toyota owner manuals](https://www.toyota.com/owners/warranty-owners-manuals/).
Последние ссылки — примеры по бренду/рынку, не подходящие мануалы для любого устройства.

## Microsoft Learn MCP

[Официальный remote MCP](https://learn.microsoft.com/en-us/training/support/mcp):
Streamable HTTP `https://learn.microsoft.com/api/mcp`, без auth и оплаты.
Инструменты: microsoft_docs_search, microsoft_docs_fetch, microsoft_code_sample_search.
На 2026-10-09 initialize/list + реальный search/fetch проверены успешно.

Если MCP уже предоставлен, используй его реальные схемы. Иначе штатный MCP-клиент
может подключить endpoint; если такой возможности нет, читай документацию через
native web либо доступный клиент в sandbox. При необходимости клиентскую SDK
установи project-local при первом вызове и переиспользуй. Новый daemon/БД/браузер
не нужен. Не правь общую конфигурацию Hermes из пользовательского sandbox.

После поиска прочитай полную важную статью через fetch. Learn не заменяет весь
consumer support Microsoft и не получает данные компьютера пользователя.
405 при открытии MCP URL обычным браузером не доказывает недоступность сервера:
он предназначен для MCP protocol, не HTML-страницы.

## Автомобильные данные

[Официальные NHTSA APIs](https://www.nhtsa.gov/nhtsa-datasets-and-apis) и
[vPIC](https://vpic.nhtsa.dot.gov/api/Home/Index) — прямой JSON-доступ без
обязательной установки MCP. Пример recalls query: make/model/modelYear по
официальной схеме. Сохрани фактические параметры, результат и источник.
Пустые/частичные ответы, decode errors и 429/5xx не означают чистую историю.
Регион и VIN-применимость проверяются отдельно; это не полный отчёт о машине.

Наш stdlib helper выполняет `nhtsa recalls` по make/model/year:
[references/official-api.md](official-api.md). Сохраняет campaign number,
components и весь исходный результат. Используй подтверждённые параметры, учитывай
американский рынок; пустая выдача не проверяет конкретный VIN и РФ.
cyanheads NHTSA MCP (2 звезды) исключён; public community relay не вызывается.

## Home Assistant и устройства

У Hermes есть native ha_list_entities, ha_get_state, ha_list_services, ha_call_service.
Используй их, если они доступны и подтверждена персональная привязка к дому.
Текущие HASS_URL/HASS_TOKEN в окружении процесса не доказывают привязку каждого
пользователя многопользовательского сервиса. Новый общий HA-сервер не нужен.

[Официальный HA MCP](https://www.home-assistant.io/integrations/mcp_server/)
дополняет существующий персональный HA через `/api/mcp` и его exposed entities/
LLM API; требует token/OAuth и сетевой доступ. Установка HA на пользователя
или второй wrapper для тех же native действий не входят в базовый workflow.

[Mobile MCP](https://github.com/mobile-next/mobile-mcp/tree/a13fba6fee9806088b3aae0ba8a9aa5e8916bbaa)
— Apache-2.0, Node >=20, real device tooling, UI/logs/apps. Проверены исходники
и зависимости, но не install/hardware E2E. Используй только при фактическом
предоставлении и проверке нужного телефона через list/devices/снимок. Не запускай
эмулятор вместо телефона пользователя и не принимай cloud fleet за его устройство.
MCP UI automation не даёт универсальный flasher или автоматический USB-туннель.

Рассмотренный OBD MCP (0 звёзд) исключён из default установки/вызовов.
Базовая ветка принимает настоящий экспорт сканера через чат. Live bridge требует
адаптера/host возле автомобиля, разрешённого доступа и проверки identity; sandbox
не заменяет подключение к автомобилю. Synthetic simulator не диагноз реальной машины.

Сторонний MCP допускается только при >1000 звёзд конкретного repo, лицензии/pin
и фактическом smoke. Mobile MCP: 8804 на 2026-10-09, проходит popularity gate;
это не подтверждение доступа к личному телефону. Обычные библиотеки и прямые
официальные API не подпадают под этот порог. Официальный Microsoft Learn remote
остаётся opt-in источником; не меняй общий runtime ради наличия справочника.

Любой device bridge проверяет identity, доступ, модель и read-only наблюдение
до изменения устройства; auth остаётся в штатном персональном подключении,
а не в выдаваемом HTML/отчёте. Первый неуспешный вызов исправляй по фактической
причине либо продолжай диалог/web. SDK installation не означает, что tools
появились в чате или что устройство стало доступно.

## iFixit

[Dthen/iFixit](https://github.com/Dthen/ifixit-mcp/tree/6b48f92906d3d15ac4eb1b6aa00fdf881aeb6902)
имеет 0BSD-код/stdlib, но [данные API](https://www.ifixit.com/api-docs) предоставлены
под BY-NC-SA; коммерческое применение требует соглашения с источником. Без него
не подключай этот API как массовый commercial default. Лицензия wrapper не
лицензирует данные. Официальные OEM-мануалы и доступные инструкции пользователя
остаются базовыми источниками.
