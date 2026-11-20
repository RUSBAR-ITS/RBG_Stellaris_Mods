# Stellaris Parser — подготовка игровых данных

## Оглавление

- [Установка](#установка)
- [Полная подготовка](#полная-подготовка)
- [Локализация](#локализация)
- [Игровые скрипты](#игровые-скрипты)

## Установка

Из корня монорепозитория в окружении Python 3.12+ установите инструмент и библиотеку формата документов. Вызовы установленного пакета работают из любого текущего каталога.

```powershell
python -m pip install ./Instruments/Document_Package ./Instruments/Stellaris_Parser
```

## Полная подготовка

Из корня монорепозитория запустите эталонный профиль WEB_STTV. При первом запуске выберите пересборку библиотек.

```powershell
python -m stellaris_parser prepare-all --config WEB_STTV/config/parser_sources.json --rebuild-libraries
```

При повторном запуске ключ `--reuse-libraries` проверяет сохранённые библиотеки. Параметр `batch.workers` ограничивает число процессов для скриптов. Ещё один процесс с начала прогона готовит словарь RU/EN. Код завершения 0 означает, что обе задачи выполнены.

В `TMP/WEB_STTV/database-inputs/artifacts/` появятся `scripts/` с раскрытыми TXT и DLC, `localization/` со словарём и `libraries/` с пятью библиотеками и манифестом. Выходные каталоги и точные пути или маски источников (`batch.sources`) задаются в профиле. [Эталонный профиль](../../WEB_STTV/config/parser_sources.json) · [Спецификация](Docs/TZ_PREPARE_ALL_RU.md)

## Локализация

Команда `prepare` принимает конфигурацию источников и каталог вывода. `localization.languages` задаёт заголовки языков и список приоритетов от высшего к низшему. `localization.directories` сопоставляет приоритет с каталогом. Относительные пути отсчитываются от файла настроек. В каталоге результата появляются `manifest.json`, `batches/` и `prepare_report.json`. [Конфигурация WEB_STTV](../../WEB_STTV/config/parser_sources.json)

```powershell
python -m stellaris_parser prepare --config WEB_STTV/config/parser_sources.json --output TMP/WEB_STTV/packages/localization
```

## Игровые скрипты

Для первого прогона из корня монорепозитория подходит пример для каталога технологий. Проверьте путь к игре в `roots`. Корень мода можно поставить первым для переопределения файлов игры. Пути вывода в конфиге отсчитываются от самого файла конфигурации. [Конфиг примера](examples/parser.json)

```powershell
$config = 'Instruments/Stellaris_Parser/examples/parser.json'
python -m stellaris_parser parse-batch --config $config --rebuild-libraries
python -m stellaris_parser parse-batch --config $config --reuse-libraries --workers 2 common/technology/tier
python -m stellaris_parser parse --config $config --reuse-libraries --output TMP/Stellaris_Parser/run-01/artifacts/physics.json common/technology/00_phys_tech.txt
```

Первый вызов подготавливает пять библиотечных JSON с манифестом в `artifacts/libraries`, затем пишет по одному раскрытому документу в `artifacts/scripts` с сохранением относительного пути исходника. В каждом основном документе есть `items` и история `metadata.expansions`. Два следующих вызова проверяют актуальность библиотек и используют их повторно. После сообщения об изменении библиотечных входов запустите пересборку.

Настройки `batch.directories`, `exclude_files`, `output` и `workers` задают каталоги, точные исключения, каталог результата и предел процессов. Пути источников и имена библиотечных файлов задаются отдельно. [Правила библиотек](stellaris_parser/config/libraries.json) · [ТЗ и критерии приёмки](Docs/TZ_BATCH_PARSE_RU.md)
