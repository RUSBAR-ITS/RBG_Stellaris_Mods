# Исследование скриптов Stellaris

## Оглавление

- [Повторный запуск](#повторный-запуск)

## Повторный запуск

Запустите команды из корня репозитория после [установки Stellaris Parser](../README_RU.md).

```powershell
$game = (Get-Content WEB_STTV/global_variables.json -Raw | ConvertFrom-Json).STELLARIS_ROOT
$tools = 'Instruments/Stellaris_Parser/tools'
foreach ($name in 'count_text','verify_frequency','audit_scalar_usage','verify_scalar_usage','audit_inline_scripts','audit_inline_payloads') {
    python -B "$tools/text_frequency/$name.py" --source $game --output TMP/WEB_STTV/text_frequency
    if ($LASTEXITCODE) { break }
}
foreach ($name in 'measure_patterns','catalog_and_verify') {
    python -B "$tools/script_patterns/$name.py" --source $game --output TMP/WEB_STTV/script_patterns
    if ($LASTEXITCODE) { break }
}
```

Для анализа мода передать его корень в `--source`. Внутри одного прогона команды группы используют общий каталог результатов. Проверки сравнивают AST с токенами, списки с манифестом текущего прогона и хеши с файлами источника. Исторические сравнения проходов 2–4 описаны в отчётах WEB_STTV. Чтобы сравнить результаты на одном корпусе с прежним проходом до фильтрации переменных, проверкам частот и скаляров можно передать его каталог через `--reference`. Аудит inline-вставок принимает в этом параметре предыдущий JSON со списком вызовов.
