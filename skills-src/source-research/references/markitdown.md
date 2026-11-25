# MarkItDown: first-use преобразование содержимого

Принят релиз [0.1.8](https://github.com/microsoft/markitdown/tree/v0.1.8), MIT,
Python >=3.10,<3.15. Это внешняя библиотека sandbox, не скопированный upstream
runtime. Наличие инструкции не означает установку в пользовательской среде.

Через coder проверь текущую project-local venv, Python и installed version.
Переиспользуй проверенную установку; отдельную .venv-documents создавай только
если среды ещё нет. Устанавливай нужные extras, например
`python -m pip install 'markitdown[docx,pptx]==0.1.8'` внутри этой среды.
Не устанавливай [all], Azure/audio extras или MCP ради одного DOCX. Не заменяй
системную среду и не добавляй глобальный сервер. При несовместимости pin проверь
поддерживаемый релиз и повтори smoke, не переходи молча на floating main.

Обычное чтение локального файла:

```python
from markitdown import MarkItDown
result = MarkItDown(enable_plugins=False).convert_local("source.docx")
markdown = result.markdown
```

Этот вызов используется bundled document_readers.py. Библиотека устанавливается
отдельно при первом вызове; portable broker tests подменяют converter fixture.
Smoke: небольшой русский DOCX с heading/table → конверсия → проверить фактические
значения и структуру. Для нужного другого формата выполнить отдельный smoke.
Не печатай содержимое конфиденциального документа в диагностику целиком.

MarkItDown преобразует содержимое для анализа; сохранение исходного DOCX layout,
правки, render QA и печатный PDF используют форматные инструменты documents.
convert_stream принимает BinaryIO, но результат — готовая строка Markdown;
не считай это доказанной потоковой постраничной обработкой.

Public MarkItDown() создаёт Magika classifier; это небольшая локальная neural
модель определения формата, не LLM. Даже базовый пакет содержит Magika dependency.
При строгом требовании «никаких локальных моделей» не объявляй обычный вызов
совместимым: нужен отдельно проверенный прямой converter/другой reader.
Не патчи библиотеку или не ставь её без обязательных зависимостей ради обхода.

Для grounded цитат обычный Markdown не гарантирует страницы. PDF извлекай с
page locators через pypdf; generic DOCX-конверсия — converted_markdown
chars/lines, а heading/paragraph/table требуют отдельного проверенного адаптера; EPUB/FB2 — главы,
spine/anchors/paragraphs. Неподтверждённые страницы не добавляй.
Скан без текста требует отдельного OCR, не считается пустым источником.
