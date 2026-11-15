# Исследование шаблона tr_purity_imperfection_remediation_wilderness

## Оглавление

- [Результат](#результат)
- [Цепочки ссылок](#цепочки-ссылок)
- [Причина диагностики](#причина-диагностики)
- [Границы проверки](#границы-проверки)

## Результат

Проверка установленной игры от 2026-11-15: файл шаблона существует **без расширения** — [common/inline_scripts/traditions/tr_purity_imperfection_remediation_wilderness](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/traditions/tr_purity_imperfection_remediation_wilderness:1). Соседнего файла с окончанием `.txt` нет.

Полное содержимое:

```text
custom_tooltip_with_modifiers = tr_purity_imperfection_remediation_wilderness_tt
```

Ссылка включена в определения трёх веток генетических традиций. Статические связи подтверждены исходниками; оснований считать путь просто неиспользуемым остатком не найдено. Формулировка прежнего отчёта об отсутствующем шаблоне относится к искомому имени с `.txt`, а не к отсутствию текста вообще.

## Цепочки ссылок

| Ветка | Включение в категорию | Традиция, подключающая общий шаблон |
| --- | --- | --- |
| Purity | [01_purity.txt:27](/E:/SteamLibrary/steamapps/common/Stellaris/common/tradition_categories/01_purity.txt:27) | [tr_purity_stage_3_swap:112](/E:/SteamLibrary/steamapps/common/Stellaris/common/traditions/01_purity.txt:112), вызов на строке 118 |
| Cloning | [01_cloning.txt:25](/E:/SteamLibrary/steamapps/common/Stellaris/common/tradition_categories/01_cloning.txt:25) | [tr_cloning_stage_3_swap:172](/E:/SteamLibrary/steamapps/common/Stellaris/common/traditions/01_cloning.txt:172), вызов на строке 178 |
| Mutation | [01_mutation.txt:26](/E:/SteamLibrary/steamapps/common/Stellaris/common/tradition_categories/01_mutation.txt:26) | [tr_mutation_stage_3_swap:95](/E:/SteamLibrary/steamapps/common/Stellaris/common/traditions/01_mutation.txt:95), вызов на строке 100 |

Все три подключают `traditions/tr_stage_3_tradition_swaps`. Его [строки 42–54](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/traditions/tr_stage_3_tradition_swaps.txt:42) содержат:

```text
tradition_swap = {
    name = tr_purity_imperfection_remediation_wilderness
    inherit_name = no
    inherit_icon = no
    trigger = {
        is_wilderness_empire = yes
    }
    inline_script = {
        script = traditions/tr_purity_imperfection_remediation_wilderness
    }
    weight = {
        factor = 1
    }
}
```

Триггер [is_wilderness_empire:1804](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:1804) проверяет `has_origin = origin_wilderness`. Дополнительная прямая ссылка есть в [01_purity.txt:198](/E:/SteamLibrary/steamapps/common/Stellaris/common/traditions/01_purity.txt:198), внутри отдельной служебной традиции с `possible = { always = no }`. Это ограничение служебной записи не отменяет цепочки из трёх категорий выше.

Ключ подсказки присутствует в [английской локализации:1375](/E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/biogenesis_l_english.yml:1375) и [русской:1097](/E:/SteamLibrary/steamapps/common/Stellaris/localisation/russian/biogenesis_l_russian.yml:1097). Текст сообщает о прибавке `+5` к максимальному размеру планеты для решения `decision_wilderness_expand`; сам найденный файл содержит только подключение подсказки, а не реализацию этой прибавки.

## Причина диагностики

При первоначальной проверке наш [загрузчик](../src/backend/sttv/script/inlining/loader.py) дописывал расширение из [inline_scripts.json](../config/parser/inline_scripts.json): `.txt`. Поэтому он искал отсутствующий вариант имени и выдавал `missing_inline_template`. По следующему поручению пользователя добавлен [отдельный конфиг исключений](../config/parser/exceptions.json), который явно разрешает чтение найденного файла без расширения. Для остальных вызовов правило `.txt` сохранено.

Ванильный [00_README.txt:33](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/00_README.txt:33) описывает вызов без расширения, а пример связывает его с файлом `.txt`. Поведение движка для файла без расширения этим примером не установлено. Автоматический поиск альтернативного имени или переименование файла в этой итерации не добавлялись.

## Границы проверки

Прочитаны определения категорий, традиций, общий шаблон, триггер происхождения, сам файл без расширения и соответствующие ключи локализации. Содержимое найденного шаблона отдельно успешно разобрано нашим парсером. Исходники игры не изменялись.

Проверка подтверждает статические ссылки и причину прежней ошибки нашего загрузчика. После подключения явного исключения все три файла традиций успешно разобраны: 75 вызовов раскрыты, четыре из них используют файл без расширения. История и JSON прошли проверки. Это изменение способа чтения в WEB_STTV; загрузка файла движком и фактическое отображение подсказки в игре по-прежнему отдельно не проверялись.
