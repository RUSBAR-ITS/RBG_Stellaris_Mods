# WEB_STTV — повторная проверка препятствий этапа 12

## Оглавление

- [Результат и границы](#результат-и-границы)
- [Подтверждённые случаи](#подтверждённые-случаи)
- [Причины в исходных конструкциях](#причины-в-исходных-конструкциях)
- [Смешанный контекст переменной Покрова](#смешанный-контекст-переменной-покрова)
- [Артефакты и следующие действия](#артефакты-и-следующие-действия)

## Результат и границы

2026-11-18 повторно проверены семь полных файлов из исторического списка этапа 9. **Все семь снова завершились теми же ошибками. Это шесть разных причин: два события используют один ошибочный шаблон `RELIC`.**

Использованы текущий код продукта, действующие конфиги и библиотеки установленной игры: `parse_text` с общим контекстом раскрытия, затем штатная статическая подстановка и сериализация, если предыдущие шаги успешны. Во всех семи случаях выполнение остановилось ещё при раскрытии; новый успешный результат БД не получен. Основной прогон занял 53,944 секунды.

Проверка ограничена этими семью документами. Разбор каждого останавливается на первой ошибке, поэтому после будущего устранения первой причины могут обнаружиться следующие. Полного повторного обхода 332 TXT новых источников с раскрытием в этой проверке не было.

Хеши всех прочитанных игровых источников проверены после прогона. Код бэкэнда, конфиги, глобальные переменные и опубликованные БД также проверены по хешам — изменений нет. Исправления не вносились. Проверка поведения движка Stellaris не выполнялась: воспроизведённая ошибка нашего инструмента сама по себе не доказывает ошибку исполнения в игре.

## Подтверждённые случаи

| Исходный документ | Ошибка | Причина |
| --- | --- | --- |
| `common/pop_jobs/06_event_jobs.txt` | `invalid_script_value_arguments` | Двойной завершающий разделитель `||` в ссылке на script value |
| `events/ancient_relics_arcsite_events_2.txt` | `unsupported_scripted_call` | Вызов `small_artifact_reward = no`; раскрыватель эффектов допускает `yes` или блок аргументов |
| `events/first_contact_dlc_operations_events.txt` | `missing_inline_parameter` | Передаётся `BONUS`, а выбранный фрагмент запрашивает `$bonus$` |
| `events/grand_archive_events.txt` | `missing_inline_parameter` | Вложенный шаблон запрашивает непереданный `RELIC` |
| `events/leviathans_events_1.txt` | `missing_inline_parameter` | Та же причина в том же шаблоне `RELIC` |
| `events/nomads_origin_events.txt` | `missing_inline_parameter` | Вызов передаёт `PERCENTAGE`, но не `RANDOM`, используемый выбранным фрагментом |
| `events/shroud_events.txt` | `ambiguous_static_environment` | Имя статической переменной собрано из частей с двумя контекстами; обработчик отвергает их без проверки совпадающего разрешения |

## Причины в исходных конструкциях

1. В [06_event_jobs.txt:2188](/E:/SteamLibrary/steamapps/common/Stellaris/common/pop_jobs/06_event_jobs.txt:2188) записано `value:scripted_modifier_mult|MODIFIER|pop_job_amenities_mult||`. Последний дополнительный `|` нарушает принятую парсером структуру закрытых пар «имя — значение». Это подтверждённое расхождение с текущей грамматикой; терпимость движка к такому окончанию не проверена.
2. В [ancient_relics_arcsite_events_2.txt:9884](/E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:9884) стоит `small_artifact_reward = no`. Определение является [scripted effect](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/archaeology_event_effects.txt:117). Запрет находится в [нашем раскрывателе](/D:/Repos/RBG_Stellaris_Mods/WEB_STTV/src/backend/sttv/script/scripted/expansion.py:49). Без отдельного исследования нельзя превращать `no` в пропуск, `yes` или отрицание эффекта.
3. Цепочка от [first_contact_dlc_operations_events.txt:330](/E:/SteamLibrary/steamapps/common/Stellaris/events/first_contact_dlc_operations_events.txt:330) до [first_contact_dlc_effects.txt:2478](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/first_contact_dlc_effects.txt:2478) передаёт `BONUS`. В [00_script_values.txt:1804](/E:/SteamLibrary/steamapps/common/Stellaris/common/script_values/00_script_values.txt:1804) условие `[[BONUS]` выбирает фрагмент, внутри которого стоит `add = $bonus$`. В действующей настройке `parameter_case_sensitive = true`, поэтому имена различаются. Это не отсутствие аргумента вообще, а несовпадение регистра. Общую регистронезависимость параметров по этому примеру не устанавливаем.
4. В [stage_3_reward_option.txt:15](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/grand_archive/collection/stage_3_reward_option.txt:15) используется `gave_relic_$RELIC$`. [Вызывающий шаблон](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/grand_archive/collection/stage_3_reward_options_by_category.txt:1) передаёт `SELECTED_RELIC` и `OTHER_RELIC_1`–`OTHER_RELIC_4`, но не `RELIC`. Соседние проверки и выдача награды используют `SELECTED_RELIC`. Сбой достигнут через `grand_archive_events.txt:4811` и `leviathans_events_1.txt:7577`; задача `VANILLA-002` уже фиксирует этот случай.
5. В [nomads_origin_events.txt:795](/E:/SteamLibrary/steamapps/common/Stellaris/events/nomads_origin_events.txt:795) вызов `pop_group_add_ethic_effect` передаёт `POP_GROUP`, `ETHOS` и `PERCENTAGE = 0.3`. В выбранной ветке [00_scripted_effects.txt:9030](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt:9030) обязательно подставляется `$RANDOM$`; аргумент и значение по умолчанию отсутствуют. Произвольно задавать ноль для прохождения проверки нельзя.

## Смешанный контекст переменной Покрова

Событие [shroud_events.txt:17815](/E:/SteamLibrary/steamapps/common/Stellaris/events/shroud_events.txt:17815) вызывает `apply_pop_template_pop_check` с `TIER = 1`; далее есть вызовы с 2 и 3. В [триггере:639](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/08_scripted_triggers_shroud.txt:639) имя составляется как `@po_apply_pop_template_tier$TIER$_nb_pop`.

Дополнительно выполнены три минимальных вызова реального триггера с неизменёнными библиотеками. Диагностическое наблюдение проверило разрешение имени отдельно в каждом найденном контексте, после чего штатный обработчик получил исходные аргументы и выдал прежнюю ошибку. Результат разрешения не подменялся.

| `TIER` | Собранное имя | Контекст шаблона | Контекст аргумента |
| ---: | --- | ---: | ---: |
| 1 | `@po_apply_pop_template_tier1_nb_pop` | 1500 | 1500 |
| 2 | `@po_apply_pop_template_tier2_nb_pop` | 3000 | 3000 |
| 3 | `@po_apply_pop_template_tier3_nb_pop` | 5000 | 5000 |

Во всех случаях нет локального переопределения, а оба контекста указывают на одно глобальное определение из [09_scripted_variables_shroud.txt:194](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_variables/09_scripted_variables_shroud.txt:194).

Причина в нашем коде: [MappedSource.environment_at](/D:/Repos/RBG_Stellaris_Mods/WEB_STTV/src/backend/sttv/script/inlining/text.py:26) сохраняет несколько контекстов у склеенного токена, а [Processor.resolve](/D:/Repos/RBG_Stellaris_Mods/WEB_STTV/src/backend/sttv/script/variables/processor.py:47) сразу отвергает кортеж контекстов. До поиска уже существующей переменной дело не доходит. Это подтверждённое ограничение парсера для данного случая; правило выбора при действительно различающихся локальных определениях ещё требуется спроектировать.

## Артефакты и следующие действия

- [Результаты семи файлов](../data/stage12/problem_recheck/results.json): коды, координаты, цепочки вызовов и трассировки.
- [Полный отчёт текущего конвейера](../data/stage12/problem_recheck/pipeline_report.json): предупреждения и хеши прочитанных источников.
- [Диагностические вызовы Покрова](../data/stage12/problem_recheck/shroud_environment_probe.json).
- Скрипты повторения: `data/stage12/problem_recheck/recheck.py` и `inspect_shroud.py`; запускать через существующее Python-окружение с `-B`.
- [ТЗ этапа 12](TZ_BACKEND_STAGE_12_RU.md) остаётся проектом. Подтверждение ошибок не означает утверждения их исправлений.

После этой проверки пользователь согласовал регистронезависимость параметров, условные исключения для четырёх исходников и `RANDOM = 0`. Последующие решения, конкретные правила и предложения по эффекту `no` и составной переменной записаны в [дополнении к импорту](SOURCE_IMPORT_EXCEPTIONS_RU.md). Они не меняют результаты приведённого выше прогона без исправлений. После реализации потребуется повторить полные файлы, а затем весь новый набор, чтобы выявить ошибки за первой точкой остановки.

[English version](RESEARCH_STAGE_12_BLOCKERS_EN.md).
