# FFmpeg в пользовательской sandbox

Основа — [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill), закреплённая ревизия `008333aaf6722083392eb6bd8bd67b59884a2a26`. Авторство и MIT-лицензия сохранены в `LICENSE.upstream`. Прочитай [references/ffmpeg/upstream-skill.md](references/ffmpeg/upstream-skill.md) перед работой: это полный исходный workflow и маршрутизация запросов на скрипты. Дополнительные справочники: [references/ffmpeg/scripts.md](references/ffmpeg/scripts.md), [references/ffmpeg/gotchas.md](references/ffmpeg/gotchas.md), [references/ffmpeg/devices.md](references/ffmpeg/devices.md).

## Runtime

Пакет каталога содержит инструкции; Python-скрипты upstream являются отдельной зависимостью среды. `skills prepare` само по себе их не устанавливает. Найди закреплённый checkout в пользовательской sandbox (обычный путь `.tools/ffmpeg-skill` в проекте), проверь его commit. При отсутствии установи в проект, сохраняя оригиналы и не меняя глобальные навыки Codex/Claude:

```sh
git init .tools/ffmpeg-skill
git -C .tools/ffmpeg-skill remote add origin https://github.com/kajisho5/ffmpeg-skill.git
git -C .tools/ffmpeg-skill fetch --depth 1 origin 008333aaf6722083392eb6bd8bd67b59884a2a26
git -C .tools/ffmpeg-skill checkout --detach FETCH_HEAD
git -C .tools/ffmpeg-skill rev-parse HEAD
```

Нужны Python 3.9+, ffmpeg и ffprobe. Закреплённый upstream имеет версию 2.5.1. Это фиксированная версия зависимости, а не предложение включить весь upstream MCP в gateway. Не меняй список инструментов concierge. В upstream-документах `<skill-dir>` и относительные пути скриптов/шаблонов означают checkout runtime, а не каталог этого адаптера.

Если `look.py` падает из-за отсутствия `drawtext`, запусти диагностику upstream по его workflow; для contact sheet допустим штатный флаг `--no-timecode`. Это сохраняет возможность визуального осмотра. Недоступный `subtitles`/libass нельзя обойти тем же флагом: прожиг титров требует подходящей сборки ffmpeg. Не устанавливай глобальную сборку на компьютере пользователя без необходимости; зависимости готовятся в его sandbox.

## Исполнение и передача

Запускай upstream-скрипты через штатный инструмент исполнения в sandbox пользователя. Следуй последовательности probe → план → обработка → check → визуальный осмотр. Читай `--help` конкретного скрипта, используй JSON-результаты; для длительного рендера — существующее фоновое исполнение. Не заменяй отсутствующий флаг выдуманной командой.

Правила upstream о сохранении исходников, пределах stream copy, HDR, dry-run и проверках обязательны. Перед отправкой проверь, что процесс завершился успешно и выходной файл существует. Передай пользователю файл штатным инструментом доставки; путь внутри контейнера сам по себе не является ссылкой для скачивания. Отчёт адаптируй к языку и стилю текущей платформы: достаточно файла, фактических параметров результата и существенных ограничений; пять английских меток upstream не обязательны. Без просмотра contact sheet не утверждай, что визуальная проверка пройдена.
