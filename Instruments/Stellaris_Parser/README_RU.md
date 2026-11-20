# Stellaris Parser — подготовка игровых данных

## Оглавление

- [Установка](#установка)
- [Локализация](#локализация)
- [Игровые скрипты](#игровые-скрипты)

## Установка

Из корня монорепозитория в окружении Python 3.12+ установите инструмент и библиотеку формата документов. Вызовы установленного пакета работают из любого текущего каталога.

```powershell
python -m pip install ./Instruments/Document_Package ./Instruments/Stellaris_Parser
```

## Локализация

Команда `prepare` принимает конфигурацию источников и каталог вывода. `localization.languages` задаёт заголовки языков и список приоритетов от высшего к низшему. `localization.directories` сопоставляет приоритет с каталогом. Относительные пути отсчитываются от файла настроек. В каталоге результата появляются `manifest.json`, `batches/` и `prepare_report.json`. [Конфигурация WEB_STTV](../../WEB_STTV/config/parser_sources.json)

```powershell
python -m stellaris_parser prepare --config WEB_STTV/config/parser_sources.json --output TMP/WEB_STTV/packages/localization
```

## Игровые скрипты

Передайте в `roots` корни выбранного мода и игры в порядке приоритета. При совпадении относительного пути используется первый файл. Для команды `parse` достаточно конфига с `roots`. Параметр `syntax_directory` позволяет выбрать другой каталог правил. Пути библиотек и кодировка заданы в `libraries.json`. Результат включает дерево с подставленными статическими переменными и метаданные раскрытия. [Правила](stellaris_parser/config/libraries.json)

```powershell
python -m stellaris_parser parse --config WEB_STTV/config/parser_sources.json --output TMP/WEB_STTV/physics.json common/technology/00_phys_tech.txt
```

Пакетный запуск и повторное использование библиотек описаны в проекте ТЗ. [ТЗ на пакетный разбор](Docs/TZ_BATCH_PARSE_RU.md)
