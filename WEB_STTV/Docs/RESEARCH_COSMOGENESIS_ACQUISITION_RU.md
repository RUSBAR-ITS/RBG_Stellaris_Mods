# Получение технологий космогенезиса и ограничения DLC

## Оглавление

- [Статус и границы](#статус-и-границы)
- [Два исследованных пути](#два-исследованных-пути)
- [Прямые выдачи и общие механизмы](#прямые-выдачи-и-общие-механизмы)
- [Влияние на текущую фильтрацию](#влияние-на-текущую-фильтрацию)
- [Дополнение по случайным выдачам](#дополнение-по-случайным-выдачам)
- [Вывод для реализации](#вывод-для-реализации)

## Статус и границы

Исследование от 2026-11-19 по запросу пользователя во время реализации [этапа 21](TZ_BACKEND_STAGE_21_RU.md). Цель — проверить получение `tech_cosmogenesis_world` и `tech_cosmogenesis_escort` прежде, чем переносить их ограничения через `has_technology`.

Исходники установленной игры: Cygnus v4.5.4 (1b4f), согласно `launcher-settings.json`. Выполнены поиск ссылок в игровых TXT, разбор определений и вызывающих цепочек, сверка с локальной документацией движка и готовой матрицей DLC. Игра не запускалась, исходники не изменены. Версия генератора локальных `effects.log` / `triggers.log` отдельно не подтверждена; это дополнительное свидетельство, а не проверка поведения движка в партии.

Исследуется штатный путь в новой партии с фиксированным набором DLC. Консольные выдачи, моды и сохранения с изменённым после получения технологий набором DLC не проверялись. Универсальный анализ всех способов получения всех технологий не выполнен.

## Два исследованных пути

| Технология | Собственные условия | Где открывается исследование |
| --- | --- | --- |
| `tech_cosmogenesis_world` | `weight = 0`; `potential`: The Machine Age **И** `has_ascension_perk = ap_cosmogenesis` | Уровень `crisis_cosmogenesis_level_1` → `on_unlock` → `add_cosmogenesis_level_1_perks` → `add_research_option` |
| `tech_cosmogenesis_escort` | `weight = 0`; `potential`: The Machine Age **И** `country_uses_bio_ships = no` | Уровень `crisis_cosmogenesis_level_2` → `on_unlock` → `add_cosmogenesis_level_2_perks` → ветвь без биологических кораблей → `add_research_option` |

Определения: [world](/E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_machine_age_tech.txt:351), [escort](/E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_machine_age_tech.txt:197). Выдача вариантов: [первый уровень](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/02_machine_age_effects.txt:15), [второй уровень](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/02_machine_age_effects.txt:29). Вызовы: [уровень 1](/E:/SteamLibrary/steamapps/common/Stellaris/common/crisis_levels/00_crisis_levels.txt:375), [уровень 2](/E:/SteamLibrary/steamapps/common/Stellaris/common/crisis_levels/00_crisis_levels.txt:397).

Оба уровня принадлежат [cosmogenesis_path](/E:/SteamLibrary/steamapps/common/Stellaris/common/crisis_paths/00_cosmogenesis_paths.txt:3). Путь активирует `ap_cosmogenesis.on_enabled`; сам бонус требует The Machine Age в `potential`: [определение бонуса](/E:/SteamLibrary/steamapps/common/Stellaris/common/ascension_perks/00_ascension_perks.txt:330). Найденный вызов `activate_crisis_progression = cosmogenesis_path` находится в этом бонусе. Триггер `has_machine_age_dlc` раскрывается в `host_has_dlc = "The Machine Age"`: [исходник](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:444).

Второй уровень дополнительно требует `tech_cosmogenesis_crisis_1` и 4000 единиц валюты кризиса. Это условия прогрессии, а не настройки DLC; они здесь не вычисляются.

`add_research_option` добавляет постоянный вариант исследования до его изучения, а не завершает исследование. Поэтому найденная цепочка объясняет получение технологии с нулевым весом: специальное открытие варианта → исследование. [Описание эффекта](</C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/logs/script_documentation/effects.log:1220>).

## Прямые выдачи и общие механизмы

- В просмотренных игровых TXT не найдены прямые выдачи этих двух ID через `give_technology` или `research_technology`. Обнаружены два указанных `add_research_option`; остальные точные ссылки проверяют наличие технологии или используют её как требование.
- `copy_random_tech_from`, применяемый при краже исследований, по локальной документации требует `weight > 0` и выполнения `potential`. Оба исследованных определения имеют нулевой вес. Поэтому этот механизм не подтверждает обход найденного ограничения. [Документация](</C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/logs/script_documentation/effects.log:1985>), [реальное применение](/E:/SteamLibrary/steamapps/common/Stellaris/events/nemesis_operations_events_1.txt:840).
- Для `copy_techs_from` документация также указывает соблюдение весов и их множителей. Само наличие массового копирования не доказывает выдачу этих технологий. [Документация](</C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/logs/script_documentation/effects.log:1805>).
- У `give_technology` описана немедленная выдача, но документация не устанавливает универсальную проверку `potential`. Для произвольной другой технологии такой эффект необходимо искать отдельно. [Документация](</C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/logs/script_documentation/effects.log:93>).
- `add_random_research_option` и служебные механизмы NPC не исследованы до доказательства всех внутренних правил движка. Отсутствие точной ссылки на ID не исключает любой динамический путь. [Описание случайного варианта](</C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/logs/script_documentation/effects.log:1971>).

Подтверждённого штатного пути получения этих двух технологий без The Machine Age не найдено. Это более узкий вывод, чем «любой ложный `potential` запрещает владеть любой технологией».

## Влияние на текущую фильтрацию

В отчёте этапа 21 оставались восемь путей к The Machine Age через эти ссылки:

| Потребители | Форма условия | Последствие |
| --- | --- | --- |
| `tech_lathe_resonator`, `tech_lathe_overclocker`, `tech_lathe_preserver`, `tech_lathe_life_support`, `tech_lathe_cogitator`, `tech_lathe_validator` | The Machine Age **И** `ap_cosmogenesis` **И** `has_technology = tech_cosmogenesis_world` | Все шесть уже имеют собственный прямой DLC-запрет. Неизвестность последнего условия не мешает скрывать их без Machine Age. |
| `tech_missiles_1`, `tech_torpedoes_1` | Обычные корабли **ИЛИ** `tr_nanotech_4` **ИЛИ** `crisis_level_2` **ИЛИ** `has_technology = tech_cosmogenesis_escort` | Запрет одного альтернативного пути не запрещает всю технологию. В справочном режиме пути для обычных кораблей сохраняются. |

Источники: [условия Латэ](/E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_machine_age_tech.txt:420), [ракеты](/E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_weapon_tech.txt:744), [торпеды](/E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_weapon_tech.txt:1038).

Проверка готовой матрицы: во всех 43 профилях без `dlc032` шесть технологий Латэ скрыты; ракеты и торпеды остаются видимыми. Это проверка текущего справочного режима без фиксированной империи. Не следует представлять восемь неразрешённых путей как восемь ошибочно показанных карточек.

## Дополнение по случайным выдачам

При реализации утверждённого дополнения выполнен обход AST общего корпуса, включая вызовы без буквального ID технологии. Для обеих целей после подтверждённых фильтров остаются четыре места `add_random_research_option` с разрешением редких технологий: `machine_age_crisis_events.txt`, `shroud_forged_events.txt`, `overlord_specialist_events.txt`, `shroud_events.txt`. Адреса команд и условия находятся в `data/stage21_acquisition/acquisition_summary.json` и графе `dlc_none_analysis.json`.

Например, [shroud_events.txt:1247](/E:/SteamLibrary/steamapps/common/Stellaris/events/shroud_events.txt:1247) использует `ignore_rare = no`. Документация перечисляет параметры отбора и их значения по умолчанию, но не подтверждает проверки `potential` и нулевого веса. Поэтому отсутствие Machine Age закрывает штатный кризисный путь, но не даёт достаточного доказательства по всем случайным путям. Итог обоих `has_technology` остаётся **unknown**, с конкретными причинами. Неизвестность не утверждает ни возможность, ни невозможность реального выпадения.

`copy_random_tech_from` и `copy_techs_from` рассматриваются отдельно по их документированным ограничениям. Для случайного варианта их правила не заимствуются. Полнота разбора источников и полнота семантики движка разделены в отчётах.

## Вывод для реализации

Подтверждённые цепочки получения проходят через DLC-зависимый бонус и уровни кризиса. Реализация связывает открытие исследования с вызывающими эффектами и условиями прогрессии; один рекурсивный обход `technology.potential` этого не заменяет. `crisis_paths` и `crisis_levels` добавлены в реестр из 30 видов БД.

По утверждённому [дополнению ТЗ](TZ_BACKEND_STAGE_21_ACQUISITION_RU.md) обработчик `has_technology` подключён к общему анализу получения, без исключений по этим ID. Результаты и границы проверки описаны в [руководстве этапа 21](BACKEND_STAGE_21_RU.md). Проверка спорной семантики в игре не выполнена.

[English version](RESEARCH_COSMOGENESIS_ACQUISITION_EN.md).
