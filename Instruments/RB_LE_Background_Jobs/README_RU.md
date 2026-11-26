# Каталог прежних профессий Leader Editor

## Оглавление

- [Исходные данные](#исходные-данные)
- [Сборка и проверка](#сборка-и-проверка)

## Исходные данные

Генератор читает утверждённые [условия видимости](../../docs/RB_LE/BACKGROUND_JOB_VISIBILITY_4_6_0_EN.csv), [реестр источников](../../docs/RB_LE/BACKGROUND_JOB_VISIBILITY_SOURCES_4_6_0_EN.csv) и определения из установленной Stellaris 4.6.0. В мод попадают игровые скрипты для отбора, подписей кнопок и назначения профессии. При обновлении игры сначала сверяют таблицы с ванилью.

## Сборка и проверка

Из корня репозитория запустить команды в среде Python, подготовленной для [Stellaris Parser](../Stellaris_Parser/README_RU.md).

```powershell
python -B Instruments/RB_LE_Background_Jobs/build.py
python -B Instruments/RB_LE_Background_Jobs/build.py --check
python -B Instruments/RB_LE_Background_Jobs/verify.py
```

По умолчанию игра читается из `E:/SteamLibrary/steamapps/common/Stellaris`. Обе команды принимают `--game ПУТЬ`. Параметр `--check` сравнивает ожидаемые игровые файлы с текущими. Проверка раскрывает шаблоны меню, сверяет кнопки с назначениями, проверяет навигацию и наличие ванильных названий в обоих языках. Условия работы населения и фактическое обновление биографии проверяются в игре. [Сценарии проверки](../../docs/RB_LE/DOSSIER_MENU_REQUIREMENTS_RU.md#условия-видимости-профессий-в-460)
