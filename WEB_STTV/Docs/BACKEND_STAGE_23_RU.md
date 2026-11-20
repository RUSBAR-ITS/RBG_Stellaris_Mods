# Этап 23 — парсер, загрузчик и сервер MongoDB

## Оглавление

- [Компоненты](#компоненты)
- [Запуск на Windows](#запуск-на-windows)
- [Чтение на Ubuntu](#чтение-на-ubuntu)
- [Публикация](#публикация)
- [Проверки](#проверки)

## Компоненты

Локальный Stellaris Parser собирает документы и назначает `_id`. Загрузчик принимает каталог пакета и публикует коллекцию. Сервер читает документ по `_id`. Первой коллекцией стала `wiki.localization`. [Парсер](../../Instruments/Stellaris_Parser/README_RU.md) · [ТЗ](TZ_BACKEND_STAGE_23_RU.md)

## Запуск на Windows

Команды выполняются из корня монорепозитория в активном окружении Python 3.12 или новее. `verify` перед первой заменой сравнивает пакет с уже опубликованным словарём. `load` полностью заменяет только коллекцию, указанную в конфигурации для данного вида пакета.

```powershell
$project = (Resolve-Path WEB_STTV).Path
$globals = Get-Content "$project/global_variables.json" -Raw | ConvertFrom-Json
$work = [IO.Path]::GetFullPath((Join-Path $project $globals.WORK_DIR))
$package = Join-Path $work 'packages/localization'

python -m pip install ./Instruments/Document_Package ./Instruments/Stellaris_Parser ./WEB_STTV/src/backend
python -m stellaris_parser prepare --config "$project/config/parser_sources.json" --output $package
python -m sttv.loader verify --config "$project/config/loader.json" --package $package
python -m sttv.loader load   --config "$project/config/loader.json" --package $package
python -m sttv.server --config "$project/config/server.json" --profile network read ru tech_titans
```

Для отдельного рабочего места загрузчика достаточно установить `Instruments/Document_Package` и `WEB_STTV/src/backend`. Пакет можно скопировать и указать любой абсолютный путь в `--package`. Профиль `network` получает пароль и открытый сертификат CA через Vault и Windows-хранилище сертификатов. Временный файл CA размещается в каталоге загрузчика. [Настройки загрузчика](../config/loader.json)

## Чтение на Ubuntu

Установите те же два пакета в окружение серверной службы. Передайте пароль `wiki` через `STTV_MONGO_PASSWORD`. В `server.json` профиль `local` выбирает `127.0.0.1:27017`, SCRAM-SHA-256 и CA `/etc/wiki-tls/ca.pem`. HTTP по умолчанию слушает `127.0.0.1:8788`. Запрос `GET /api/localization/ru/tech_titans` возвращает документ с `selected` и `definitions`. Отсутствующий ключ даёт HTTP 404. [Настройки сервера](../config/server.json)

```sh
python -m sttv.server --config /path/to/server.json read en tech_titans
python -m sttv.server --config /path/to/server.json serve
```

## Публикация

`manifest.json` содержит формат `stellaris.documents.v1`, логическое имя коллекции, общее число документов и упорядоченный список файлов с числом записей и SHA-256. Загрузчик сверяет хеши при чтении, пишет в отдельную временную коллекцию и сравнивает документы по типизированному BSON `_id`. Для составного ключа значим порядок полей. После полной сверки MongoDB атомарно переименовывает коллекцию. При ошибке публикации предыдущая коллекция доступна читателям.

## Проверки

На Windows обработано 706 файлов и 453 781 определение. Сверка с исходной коллекцией, две публикации и повторная сверка прошли для всех 303 500 документов. Хеши файлов перенесённого пакета до и после совпали. На Ubuntu через `local` и на Windows через `network` выполнено чтение. Для `tech_titans` получены «Титаны» и `Titans`. На отдельной коллекции проверены строковый `_id`, вложенные значения, перестановка пакетов, дубли, повреждение файла и удаление устаревшей записи. На фикстурах фронтенда прошли 71 модульная и 24 браузерные проверки. Девять браузерных и четыре модульных сценария требуют прежних входных файлов и пропущены.

Парсер установлен отдельно от WEB_STTV и PyMongo. Проверен выбор файла мода по приоритету, вложенное раскрытие и подстановка переменной. В ванильном `00_phys_tech.txt` разобраны 69 верхнеуровневых записей и 132 раскрытия. Загрузчик также установлен отдельно и выполнил полную сверку без установленного парсера.

В проверке прежнего файлового дерева `test_publication_reuse_force_and_other_inputs_unchanged` осталось расхождение. Тест ожидает 24 непрочитанных документа. Фикстура создаёт 30 документов, из которых повторный вызов читает один и отмечает остальные 29 как непрочитанные.
