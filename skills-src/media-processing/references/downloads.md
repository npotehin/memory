# Практические команды

Команды выполняются в папке проекта. Подставляй URL как отдельный аргумент; при программном запуске используй список аргументов subprocess, без shell-интерполяции пользовательского текста.

## Осмотр

```sh
yt-dlp --no-playlist --dump-single-json -- 'URL' > metadata.json
yt-dlp --no-playlist --list-formats -- 'URL'
yt-dlp --no-playlist --list-subs -- 'URL'
```

JSON может содержать служебные signed URL: не публикуй его целиком без проверки.
Сохраняй код завершения yt-dlp: не маскируй его командой `yt-dlp ... | tail`.
Для сокращения вывода сохрани лог отдельно и прочитай его после завершения;
при использовании конвейера нужен shell с `pipefail`. Нулевой код shell без
готового файла и проверки ffprobe не подтверждает успешное скачивание.

## Видео и аудио

```sh
yt-dlp --no-playlist -f 'bv*+ba/b' -S 'res:1080' \
  -o 'downloads/%(id)s.%(ext)s' -- 'URL'
yt-dlp --no-playlist -f 'bestaudio/best' -x --audio-format mp3 \
  --audio-quality 0 -o 'downloads/%(id)s.%(ext)s' -- 'URL'
```

Первый рецепт выбирает качество до предпочтительных 1080p, но не обещает MP4/H.264. Для обычного мобильного просмотра после получения проверь контейнер и кодеки; при необходимости используй ffmpeg для MP4/H.264/AAC. Не увеличивай разрешение низкокачественного источника.

## Субтитры без видео

```sh
yt-dlp --no-playlist --skip-download --write-subs --write-auto-subs \
  --sub-langs 'ru.*,en.*' --sub-format 'vtt/best' \
  -o 'downloads/%(id)s.%(ext)s' -- 'URL'
```

Выбери нужный язык из полученных файлов, различай авторские и автоматические субтитры. При суммаризации сохраняй таймкоды и не объявляй ASR-текст точной цитатой без сверки аудио.

## Плейлист и повторный запуск

```sh
yt-dlp --flat-playlist --dump-single-json -- 'PLAYLIST_URL' > playlist.json
yt-dlp --yes-playlist --playlist-end 10 --download-archive archive.txt \
  -o 'downloads/%(playlist_index)03d-%(id)s.%(ext)s' -- 'PLAYLIST_URL'
```

`--playlist-end 10` здесь пример явно ограниченной подборки; подставь согласованный диапазон. Archive предотвращает повторное скачивание уже готовых элементов. Не выдавай частично скачанный `.part` за итоговый файл.

Актуальные extractor-зависимости, поддержка JS runtimes и флаги: https://github.com/yt-dlp/yt-dlp#readme
