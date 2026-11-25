# Источники РФ и опциональные интеграции

## Базовый доступ без платных API-ключей

Личные данные приходят от пользователя: CSV/XLSX, PDF с текстовым слоем,
подтверждённый ручной ввод. Сначала переиспользуй `documents`, `spreadsheets`,
native execution/web/browser и sender. Не разворачивай финансовое приложение
только ради разбора выписки и не добавляй финансовые библиотеки в gateway.

Инструкцию выгрузки уточняй по банку/типу счёта/текущему интерфейсу. Проверенные
официальные примеры, не обещание универсального CSV:

- [Т-Банк: выписка по счёту Junior, PDF](https://www.tbank.ru/bank/help/debit-cards/junior/get-statement/account-statement/).
- [Альфа-Банк: справки/выписки по дебетовой карте](https://alfabank.ru/help/t/retail/debitcards/alfacard/kak-polzovatsya-kartoi/kak-poluchit-spravku-ili-vipisku-po-debetovoi-karte/).
- [ВТБ: выписка по кредитной карте](https://www.vtb.ru/articles/kreditnye-karty/vypiska-po-kreditnoy-karte/).

Бизнес-API банка не является универсальным retail-доступом: пример
[Alfa API выписок ЮЛ](https://developers.alfabank.ru/products/alfa-api/documentation/articles/transactions/articles/intro/v1/intro)
прямо относится к юридическим лицам. Не превращай API бизнес-выписок в обещание
автоматически подключить личную карту. Банковские login/OTP вводит пользователь
в штатном банковском интерфейсе; skill не собирает их в чат/конфиг.

## Официальные данные для расчётов

| Источник | Что использовать | Ограничение |
|---|---|---|
| [ЦБ: XML API](https://www.cbr.ru/development/sxml/) | Курсы на дату/история, справочник валют, цены металлов | `Value / Nominal`, фактическая дата действия; официальный курс не retail обмен |
| [ЦБ: ключевая ставка](https://www.cbr.ru/hd_base/KeyRate/) | Датированная справочная ставка | Не ставка кредита/вклада конкретного банка |
| [ЦБ: инфляция](https://www.cbr.ru/hd_base/infl/) | Сопоставимый макроконтекст, опубликованная инфляция г/г | Не личная инфляция и не накопленный CPI произвольного периода |
| [ФНС: вычеты](https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/nalog_vichet/) | Правила, перечень документов на конкретный налоговый период | Проверка статуса/условий; не гарантия возврата |
| [MOEX: ISS](https://www.moex.com/en/documents/8888), [справочник](https://iss.moex.com/iss/reference/) | Публичные справочники/история/поля инструмента для информационного разбора | Доступ/задержка/права зависят от набора; нет личного портфеля или банковских операций |

Публичные read-only requests на HTTPS можно выполнять обычным HTTP-клиентом:
`https://www.cbr.ru/scripts/XML_daily.asp?date_req=08/10/2026`,
`https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=01/10/2026&date_req2=08/10/2026&VAL_NM_RQ=R01235`,
`https://iss.moex.com/iss/securities/SBER.json?iss.meta=off&iss.only=description`.
Это примеры фиксированной даты/справочника, не текущая котировка.

XML читай как bytes с учётом объявленной кодировки; деньги — Decimal из строк
с заменой запятой. MOEX columns/data сопоставляй по именам колонок; учитывай
board, валюту, лот и pagination истории. Сохраняй URL/параметры/время/дату данных,
не подставляй последнее значение вместо недоступного исторического без пометки.
Нет ответа → источник недоступен, не нулевой курс/котировка. Cache используй
по валюте/дате/источнику. Не выключай TLS verification.

## OSS/MCP: подключать по реальной необходимости

**Actual Budget:** идеи envelope budgets, rules, reconciliation, filters и
reports полезны для своего workflow. [API](https://actualbudget.org/docs/api/)
работает через `@actual-app/api` с локальной копией бюджета, а не универсальный
bank REST. [Bank sync](https://actualbudget.org/docs/advanced/bank-sync/)
требует server/provider credentials; перечисленные провайдеры не заявляют РФ.
MCP не добавляет российские банки к этим провайдерам.

Если пользователь уже ведёт Actual, используй официальный `@actual-app/api`
в project-local Node окружении: init с личным dataDir/serverURL/password →
downloadBudget с подтверждённым sync ID → read-only getAccounts/getTransactions/
getBudgetMonth → shutdown в finally. Нужен личный writable cache; E2E-password
передаётся только штатным секретным окружением. Проверяй методы текущей закреплённой
версии SDK по документации; не выдумывай REST endpoint или Python замену sync
protocol. Это единственная Node-ветка, поскольку официальный SDK требует Node.
agigante80/actual-mcp-server ниже порога и не устанавливается. Live личный budget
не проверен без авторизованной системы пользователя.

**Firefly III:** существующий личный instance читается собственным Python helper:
`firefly accounts/transactions/categories/budgets`, page/limit/start/end/id.
[API contract](https://github.com/firefly-iii/api-docs),
[references/official-api.md](official-api.md). FIREFLY_URL/TOKEN только через
персональное credential path; настоящий readback подтвердит owner/счёт. Не
сохраняй token в выгрузку/HTML. API schema сверяй с версией самого instance.
Сохраняй pagination, currencies, split transactions и transfer/refund semantics.
Скрипт не записывает операции и не подключает банк. daften/fireflyiii-mcp ниже
порога и не устанавливается; новое PHP/БД приложение ради выписки не нужно.

**ЦБ/MOEX:** наш helper реализует `cbr rates` (ISO date, Decimal Value/Nominal,
фактическая дата) и `moex security` (описание/доски, columns/data). История,
ключевая ставка, инфляция и ФНС остаются прямыми официальными запросами/native web
по контрактам выше; этим двум действиям не приписывай остальные API возможности.
Сторонние ru-finance/mcp-moex исключены: ниже порога и неясная лицензия.

GitHub-порог >1000 относится только к сторонним MCP, не к обычным библиотекам.
Официальные API разрешены. Новый MCP проверяй по своему repo, pinned license/runtime,
персональной привязке и реальному read-only запросу. Звёзды Actual/Firefly не
разрешают отдельный wrapper. No paid key не отменяет auth; тест fixture не доказывает
личный live sync. Платёжные/trade tools не нужны.
