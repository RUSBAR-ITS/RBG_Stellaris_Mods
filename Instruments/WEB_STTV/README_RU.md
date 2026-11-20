# Исследовательские инструменты WEB_STTV

## Оглавление

- [Запуск на снимке](#запуск-на-снимке)

## Запуск на снимке

Запуск из корня монорепозитория с установленными зависимостями бэкенда. В примере `$variables` — файл переменных для подготовленного набора, а его `WORK_DIR` указывает на родительский каталог `database_set/`. Подставить фактический путь.

```powershell
$env:PYTHONPATH = (Resolve-Path WEB_STTV/src/backend).Path
$variables = 'TMP/WEB_STTV/variables.json'
$configuredWork = (Get-Content $variables -Raw | ConvertFrom-Json).WORK_DIR
$work = [IO.Path]::Combine((Resolve-Path WEB_STTV).Path, $configuredWork)
$tools = 'Instruments/WEB_STTV'
python -B "$tools/empire_parameters/inventory.py" --snapshot "$work/database_set" --output "$work/empire_parameters"
python -B "$tools/empire_parameters/classify.py" --output "$work/empire_parameters"
python -B "$tools/dlc/accept_stage21.py" --variables $variables --output "$work/dlc_matrix"
python -B "$tools/dlc/check_acquisition.py" --variables $variables --profiles "$work/dlc_matrix/matrix.json" --output $work
```

Для проверки публикации выполнить на тестовом снимке следующую команду. Она изменяет комбинации в переданном наборе и создаёт `publication.json` рядом с `matrix.json` для фронтенд-теста.

```powershell
python -B "$tools/dlc/publish_acquisition.py" --variables $variables --output $work
```
