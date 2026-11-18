# Stellaris Technological Tree View — разбор 39 неоднозначных продолжений

## Оглавление

- [Область исследования](#область-исследования)
- [Результаты проверки признаков](#результаты-проверки-признаков)
- [Идея сохранения самостоятельных цепочек](#идея-сохранения-самостоятельных-цепочек)
- [Прямые связи улучшения объектов](#прямые-связи-улучшения-объектов)
- [Разбор всех случаев](#разбор-всех-случаев)
- [Предложения для обсуждения](#предложения-для-обсуждения)
- [Материалы и проверка](#материалы-и-проверка)

## Область исследования

Исследование от 2026-11-17 по просьбе пользователя. Рассмотрены все 39 технологий, у которых после отбора пререквизитов по совпадающим `area` и `category` остаётся несколько кандидатов. Основной источник — `data/stage10/database.json`.

Локализованные названия, общая часть ID и числовые суффиксы не используются для определения продолжений. ID служат непрозрачными ключами ссылок. Названия в таблице приведены только для чтения.

Дополнительно прочитаны определения компонентов и зданий установленной игры, а для отдельных случаев — вызываемые ими скрипты и другие объекты. Эти дополнительные данные отсутствуют в текущей технологической БД. БД, код продукта и игровые файлы не менялись. Результаты ниже — наблюдения и предложения, не новые утверждённые правила сортировки.

Последующее решение пользователя от 2026-11-17: приоритет обязательного пререквизита согласован как [L-08](TECHNOLOGY_CHAINS_AND_SORTING_RU.md#приоритет-обязательного-пререквизита). Он разрешает ещё пять случаев: вместе с 21 случаем, поддержанным улучшениями объектов или совпадающими эффектами, основания для выбора имеются у 26 технологий; 13 остаются неоднозначными. Формулировки о возможном правиле в исходной таблице отражают исследование до этого решения. Для программной работы с улучшениями отдельно определена необходимость БД компонентов и зданий и поддержки трёх БД во фронтенде.

## Результаты проверки признаков

| Признак | Результат по 39 случаям | Ограничение |
| --- | --- | --- |
| Предпочесть пререквизит с наибольшим `tier` | Единственный кандидат у 19 | Для форсажных камер выбирает двигатели; для усилителей реактора — реактор. Не определяет семейство. |
| У предшественника нет другого продолжения с единственным кандидатом по области и категории | Единственный кандидат у 19 | У разумных боевых компьютеров выбирает ИИ, хотя явное улучшение компонентов ведёт от предыдущих боевых компьютеров. |
| У предшественника только один зависимый узел той же области и категории | Единственный кандидат у 24 | Для дюрастальных сплавов выбирает `tech_alloys_2`, хотя одинаковый производственный модификатор связывает их с предыдущей технологией металлургии. |
| Совпадение ключей реальных модификаторов | Единственный кандидат у 6 | Полезное свидетельство общих эффектов; у большинства технологий эффект задаётся открываемыми объектами, а не собственным `modifier`. |
| Совпадение непустой структуры `potential` | Единственный кандидат у 14 | Общие ограничения доступа не равны общему семейству. В том числе совпадает нежелательный кандидат ИИ для боевых компьютеров. |
| `gateway`, `feature_flags`, `weight_groups` | Ни одного различающего продолжение совпадения | У всех 39 отсутствует `gateway`; собственный `feature_flags` есть только у мегапроектирования; `weight_groups` есть у двух повторяемых технологий. |
| Единственный непосредственно обязательный пререквизит среди подходящих кандидатов | 5 из 11 случаев с `OR` | Может быть основанием для предпочтения в раскладке. Игра не объявляет его главным продолжением семейства. |
| Явное улучшение открываемого компонента или здания | Подтверждены пары для 16 технологий: 12 через компоненты, 4 через здания | Требует дополнительных каталогов; положительное свидетельство, а не полный аудит всех возможных открываемых объектов. |

Совпадение модификаторов проверялось по точным ключам, без анализа их словесного сходства. Служебные `description`, `custom_tooltip` и параметры описаний не считаются игровыми эффектами. Шесть совпадений: `tech_advanced_metallurgy_2`, `tech_consumer_good_refinement_2`, `tech_cryostasis_2`, `tech_habitat_3`, `tech_robomodding_points_2`, `tech_xeno_relations`. Совпадения модификаторов и прямые улучшения объектов пересекаются, поэтому их количества нельзя складывать без устранения повторов.

Для `tech_capital_productivity_3` найдено отдельное подтверждение вне технологического объекта: в `common/inline_scripts/buildings/on_all_capital_buildings.txt:69` последовательные условия технологий переключают `pop_bonus_workforce_mult` с 0.05 на 0.10 и 0.15 с учётом уровня столицы. Это поддерживает продолжение от `tech_capital_productivity_2`. В самой технологии записан только ключ описания этого эффекта.

## Идея сохранения самостоятельных цепочек

Пример пользователя подтверждается структурой:

```text
tech_thrusters_1 -> tech_thrusters_2 -> tech_thrusters_3 -> tech_thrusters_4
        |
        +--------> tech_afterburners_1 -----------------> tech_afterburners_2

Additional requirement: tech_thrusters_3 -> tech_afterburners_2
```

У `tech_thrusters_4` единственный пререквизит — `tech_thrusters_3`. У `tech_afterburners_1` единственное продолжение — `tech_afterburners_2`. Сохранение обоих продолжений позволяет не обрывать двигательную и форсажную ветви.

Проверены два варианта этой идеи:

1. **Локальное исключение занятого предшественника.** Для каждого узла найдены зависимые технологии, у которых он единственный кандидат после отбора по области и категории. При нескольких пререквизитах предпочтён тот, у которого таких других продолжений нет. В 19 случаях остаётся один кандидат. Это эвристика, а не доказательство принадлежности ветви.
2. **Совместный выбор продолжений по всему графу.** Экспериментальная цель — сохранить максимально возможное число продолжений, разрешая каждой технологии не более одного основного входящего и одного основного исходящего продолжения. Остальные зависимости остаются дополнительными связями. Среди 679 технологий и 483 подходящих связей максимум составляет 294 продолжения, или 385 путей с учётом одиночных вершин. Проверены не только один полученный вариант, но возможность каждого родителя и отдельного начала пути при том же максимуме. В 18 из 39 случаев родитель одинаков во всех оптимальных вариантах.

Оба способа выбирают `tech_afterburners_1` для `tech_afterburners_2`. Но оба выбирают `tech_sapient_ai` для `tech_combat_computers_3`: предыдущий боевой компьютер также открывает самостоятельное продолжение `tech_combat_computers_autonomous`. При этом в компонентах прямо задано улучшение обычного продвинутого компьютера в разумный. Сохранение наибольшего числа путей само по себе не гарантирует сохранение игровых семейств.

Дополнительный пример: глобальный эксперимент присоединяет мегапроектирование к кораблю-ковчегу, поскольку это выгодно для числа сохранённых путей. Такой геометрический результат не доказывает, что мегапроектирование является следующим уровнем корабля-ковчега.

Эти эксперименты рассматривают листья `OR` как допустимые связи размещения и не вычисляют условия государства. Их числовые результаты не означают, что найдены 18 или 19 подтверждённых игровых цепочек.

## Прямые связи улучшения объектов

Для форсажных камер в `common/component_templates/00_utilities_afterburners.txt` задано:

```text
utility_component_template = {
    key = "AFTERBURNER_1"
    prerequisites = { "tech_afterburners_1" }
    upgrades_to = "AFTERBURNER_2"
}

utility_component_template = {
    key = "AFTERBURNER_2"
    prerequisites = { "tech_afterburners_2" }
}
```

Это сокращённые фрагменты определения: остальные поля опущены. Связь установлена по точному значению `upgrades_to` и пререквизитам объектов, а не по сходству их ID. В зданиях аналогичный источник — список `upgrades`.

Прямой просмотр 83 файлов компонентов и зданий дал 1892 объекта и 60 свидетельств таких улучшений для 16 рассматриваемых технологий. Несколько свидетельств могут относиться к разным размерам или видам компонентов одной технологии. В этом дополнительном проходе 1626 inline-вызовов структурно обнаружены, но не раскрывались. Поэтому отсутствие свидетельства в таблице не доказывает отсутствие любых внешних связей; учитываются только явно прочитанные верхнеуровневые улучшения с одним скалярным технологическим пререквизитом на каждом конце.

## Разбор всех случаев

В столбце кандидатов перечислены только пререквизиты с совпадающими областью и категорией. Исходные требования, включая остальные области и `OR`, сохранены в исследовательском JSON. «Предпочтение» ниже описывает результат конкретного признака и не утверждает новое правило.

| № | Технология | Кандидаты | Наблюдение |
| ---: | --- | --- | --- |
| 1 | Металлокерамические сплавы — `tech_advanced_metallurgy_1` | `tech_alloys_1`; `tech_ship_armor_2` | Оба кандидата имеют собственные продолжения. Новый модификатор производства металлургов не совпадает с эффектами родителей; начало отдельной ветви выглядит обоснованнее автоматического выбора одного из них, но это предложение. |
| 2 | Дюрастальные сплавы — `tech_advanced_metallurgy_2` | `tech_advanced_metallurgy_1`; `tech_alloys_2`; `tech_ship_armor_4` | `tech_advanced_metallurgy_1`: единственный кандидат с совпадающими ключами реальных модификаторов. |
| 3 | Улучшенные форсажные камеры — `tech_afterburners_2` | `tech_afterburners_1`; `tech_thrusters_3` | `tech_afterburners_1`: явное улучшение компонента [AFTERBURNER_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_afterburners.txt:24) → [AFTERBURNER_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_afterburners.txt:63). |
| 4 | Матрица подпространственной визуализации — `tech_arkship_system_scanner` | `tech_sensors_2`; `tech_automated_exploration` | Оба структурных эксперимента выбирают `tech_automated_exploration`. Открывается самостоятельный модуль ковчега (`common/starbase_modules/00_arkship_spinal_modules.txt:197`); прямого улучшения от объектов кандидатов не установлено. |
| 5 | Инженерия корабля-ковчега — `tech_arkship_tier_2` | `tech_cruisers`; `tech_arkship_construction` | `tech_arkship_construction` обязателен напрямую; остальные подходящие кандидаты входят в `OR`. Предпочтение обязательного — возможное правило размещения, не метка семейства игры. |
| 6 | Совершенный корабль-ковчег — `tech_arkship_tier_3` | `tech_battleships`; `tech_arkship_tier_2` | `tech_arkship_tier_2` обязателен напрямую; остальные подходящие кандидаты входят в `OR`. Предпочтение обязательного — возможное правило размещения, не метка семейства игры. |
| 7 | Закалка брони — `tech_armor_hardeners_1` | `tech_advanced_metallurgy_1`; `tech_rare_crystals` | Начало найденной компонентной цепочки закалки брони. Правило единственного зависимого узла выбирает `tech_rare_crystals`, но подтверждённого улучшения от открываемых родителями объектов нет. |
| 8 | Адаптивная закалка брони — `tech_armor_hardeners_2` | `tech_armor_hardeners_1`; `tech_mine_living_metal` | `tech_armor_hardeners_1`: явное улучшение компонента [ARMOR_HARDENER_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:250) → [ARMOR_HARDENER_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:284). |
| 9 | Максимальная продуктивность — `tech_capital_productivity_3` | `tech_galactic_administration`; `tech_capital_productivity_2` | `tech_capital_productivity_2`: внешние условия последовательно меняют тот же `pop_bonus_workforce_mult`; см. пример выше. Собственный `modifier` технологии содержит лишь описание. |
| 10 | Улучшенные маскировочные поля — `tech_cloaking_2` | `tech_cloaking_1`; `tech_shields_3` | `tech_cloaking_1`: явное улучшение компонента [CORVETTE_CLOAKING_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux_first_contact.txt:10) → [CORVETTE_CLOAKING_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux_first_contact.txt:87). |
| 11 | Превосходные маскировочные поля — `tech_cloaking_3` | `tech_cloaking_2`; `tech_shields_4` | `tech_cloaking_2`: явное улучшение компонента [CORVETTE_CLOAKING_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux_first_contact.txt:87) → [CORVETTE_CLOAKING_3](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux_first_contact.txt:173). |
| 12 | Маскировочные поля из тёмной материи — `tech_cloaking_dark_matter` | `tech_dark_matter_deflector`; `tech_cloaking_3` | `tech_cloaking_3`: явное улучшение компонента [SCIENCE_CLOAKING_3](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux_first_contact.txt:1249) → [SCIENCE_CLOAKING_DARK_MATTER](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux_first_contact.txt:1274). |
| 13 | Расширенные боевые алгоритмы — `tech_combat_computers_2` | `tech_combat_computers_1`; `tech_self_aware_logic` | `tech_combat_computers_1`: явное улучшение компонента [COMBAT_COMPUTER_SWARM_BASIC](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_roles.txt:297) → [COMBAT_COMPUTER_SWARM_ADVANCED](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_roles.txt:339). |
| 14 | Разумные боевые симуляторы — `tech_combat_computers_3` | `tech_combat_computers_2`; `tech_sapient_ai` | `tech_combat_computers_2`: явное улучшение компонента [COMBAT_COMPUTER_SWARM_ADVANCED](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_roles.txt:339) → [COMBAT_COMPUTER_SWARM_SAPIENT](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_roles.txt:381). |
| 15 | Прогноз потребления — `tech_consumer_good_refinement_2` | `tech_consumer_good_refinement_1`; `tech_self_aware_logic` | `tech_consumer_good_refinement_1`: единственный кандидат с совпадающими ключами реальных модификаторов. |
| 16 | Колониальные корабли с самосознанием — `tech_cryostasis_2` | `tech_self_aware_logic`; `tech_cryostasis_1` | `tech_cryostasis_1`: единственный кандидат с совпадающими ключами реальных модификаторов. |
| 17 | Тахионные копья — `tech_energy_lance_2` | `tech_lasers_5`; `tech_energy_lance_1` | `tech_energy_lance_1`: явное улучшение компонента [ENERGY_LANCE_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_extra_large.txt:6) → [ENERGY_LANCE_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_extra_large.txt:73). |
| 18 | Комплекс производства роботов — `tech_fe_assembly_1` | `tech_robomodding`; `tech_robomodding_m` | `OR` двух разных технологий робомодификации. Ни одна не обязательна сама по себе; обоснованное единственное продолжение не найдено. |
| 19 | Генное здравоохранение — `tech_frontier_health` | `tech_basic_health`; `tech_genome_mapping` | `tech_basic_health`: явное улучшение здания [building_medical_1](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/07_amenity_buildings.txt:732) → [building_medical_2](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/07_amenity_buildings.txt:826). |
| 20 | Камера роста — `tech_growth_chamber_1` | `tech_stingers`; `tech_mauler_growth_1`; `tech_stinger_growth_1`; `tech_weaver_growth_1`; `tech_harbinger_growth_1` | `tech_stingers` обязателен напрямую; остальные подходящие кандидаты входят в `OR`. Предпочтение обязательного — возможное правило размещения, не метка семейства игры. |
| 21 | Передовая камера роста — `tech_growth_chamber_2` | `tech_growth_chamber_1`; `tech_mauler_growth_2`; `tech_stinger_growth_2`; `tech_weaver_growth_2`; `tech_harbinger_growth_2` | `tech_growth_chamber_1` обязателен напрямую; остальные подходящие кандидаты входят в `OR`. Предпочтение обязательного — возможное правило размещения, не метка семейства игры. |
| 22 | Расширение орбитальных поселений — `tech_habitat_2` | `tech_habitat_1`; `tech_starbase_4` | `tech_habitat_1`: явное улучшение здания [building_hab_capital](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/00_capital_buildings.txt:1010) → [building_hab_major_capital](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/00_capital_buildings.txt:1146). |
| 23 | Улучшенные орбитальные поселения — `tech_habitat_3` | `tech_habitat_2`; `tech_starbase_5` | `tech_habitat_2`: явное улучшение здания [building_hab_major_capital](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/00_capital_buildings.txt:1146) → [building_hab_system_capital](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/00_capital_buildings.txt:1292). |
| 24 | Джаггернаут — `tech_juggernaut` | `tech_starbase_5`; `tech_arkship_construction`; `tech_battleships` | Объединение двух групп `OR`. Глобальная оптимизация выбирает `tech_starbase_5`, но явное продолжение семейства этим не подтверждается. |
| 25 | Кинетическая артиллерия — `tech_kinetic_artillery_2` | `tech_mass_drivers_5`; `tech_kinetic_artillery_1` | `tech_kinetic_artillery_1`: явное улучшение компонента [KINETIC_ARTILLERY_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_projectile.txt:916) → [KINETIC_ARTILLERY_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_projectile.txt:984). |
| 26 | Гигапушка — `tech_mass_accelerator_2` | `tech_mass_drivers_5`; `tech_mass_accelerator_1` | `tech_mass_accelerator_1`: явное улучшение компонента [MASS_ACCELERATOR_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_extra_large.txt:282) → [MASS_ACCELERATOR_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_extra_large.txt:360). |
| 27 | Мегапроектирование — `tech_mega_engineering` | `tech_starbase_5`; `tech_arkship_tier_3`; `tech_battleships` | Сведение нескольких ветвей и двух групп `OR`. Оптимизация выбирает `tech_arkship_tier_3` ради числа путей; собственные эффекты отличаются от эффектов кандидатов. |
| 28 | Боевые корабли-ковчеги — `tech_military_arkship` | `tech_destroyers`; `tech_arkship_construction` | `tech_arkship_construction` обязателен напрямую; остальные подходящие кандидаты входят в `OR`. Предпочтение обязательного — возможное правило размещения, не метка семейства игры. |
| 29 | Модульное проектирование — `tech_modular_engineering` | `tech_starbase_3`; `tech_waystation_2` | `OR` космической базы и маршрутной станции. Новые модификаторы стоимости строительства не совпадают с модификаторами родителей; единственной исходной цепочки нет в проверенных признаках. |
| 30 | Улучшенные усилители реактора — `tech_reactor_boosters_2` | `tech_fusion_power`; `tech_reactor_boosters_1` | `tech_reactor_boosters_1`: явное улучшение компонента [REACTOR_BOOSTER_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:4) → [REACTOR_BOOSTER_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:29). |
| 31 | Продвинутые усилители реактора — `tech_reactor_boosters_3` | `tech_antimatter_power`; `tech_reactor_boosters_2` | `tech_reactor_boosters_2`: явное улучшение компонента [REACTOR_BOOSTER_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:29) → [REACTOR_BOOSTER_3](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:54). |
| 32 | Контроль термодинамического выхода — `tech_repeatable_weapon_type_explosive_damage` | `tech_missiles_3`; `tech_swarmer_missiles_2` | Повторяемое усиление взрывного оружия после `OR` двух технологий. Локальная эвристика выбирает `tech_swarmer_missiles_2`; глобальный выбор допускает разные варианты, включая отдельный путь. |
| 33 | Миниатюрные воспламенители — `tech_repeatable_weapon_type_explosive_fire_rate` | `tech_missiles_3`; `tech_swarmer_missiles_2` | Та же структура альтернатив, что у усиления урона; отдельный модификатор скорострельности. Локальная эвристика снова выбирает `tech_swarmer_missiles_2`, создавая конкуренцию за продолжение. |
| 34 | Кросс-модельная стандартизация — `tech_robomodding_points_1` | `tech_robomodding`; `tech_droid_workers` | Новые модификаторы очков признаков не совпадают с эффектами родителей. У обоих есть собственные продолжения; выбор одного потребует дополнительного основания. |
| 35 | Взаимозаменяемые схемы — `tech_robomodding_points_2` | `tech_robomodding_points_1`; `tech_synthetic_workers` | `tech_robomodding_points_1`: единственный кандидат с совпадающими ключами реальных модификаторов. |
| 36 | Инженерные войска — `tech_space_defense_station_improvement` | `tech_starbase_4`; `tech_modular_engineering` | Оба структурных эксперимента предпочитают `tech_modular_engineering`. Модификаторы стоимости/скорости улучшения отличаются от модификаторов строительства родителя; пока структурный кандидат. |
| 37 | Метакогнитивная вера — `tech_transcendent_faith` | `tech_consecration_fields`; `tech_galactic_administration` | `tech_consecration_fields` выделяется по единственному зависимому узлу и совпадающему `potential`. Открываемые здания не соединены найденным прямым `upgrades`; подтверждение неполное. |
| 38 | Вулканическое терраформирование — `tech_volcanic_terraforming` | `tech_terrestrial_sculpting`; `tech_volcano` | Структура предпочитает `tech_volcano`. Однако новая технология используется в `common/terraform`, а второй кандидат открывает терраформирование. Одного числа продолжений для определения семейства недостаточно. |
| 39 | Ксеноотношения — `tech_xeno_relations` | `tech_xeno_diplomacy`; `tech_galactic_administration` | `tech_xeno_diplomacy`: явное улучшение здания [building_embassy](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/02_government_buildings.txt:763) → [building_grand_embassy](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/02_government_buildings.txt:843). |

## Предложения для обсуждения

- Использовать явное улучшение открываемых объектов как сильное подтверждение продолжения: сначала проверить точные ссылки, затем соотнести технологические пререквизиты.
- Совпадение реальных модификаторов использовать как дополнительное свидетельство общих эффектов, не выводить его из названия или текстового описания.
- Согласовано как L-08: предпочитать обязательный пререквизит участнику альтернативной группы среди кандидатов по L-07. Сохранять саму группу `OR` и все игровые связи.
- Идею пользователя о сохранении самостоятельных ветвей использовать с учётом подтверждённых продолжений. Не считать любое другое зависимое исследование доказательством, что предшественник уже «занят».
- Разрешить обсуждение отдельного начала ветви в точке объединения нескольких семейств. Для собственно раскладки всё равно потребуется согласовать, возле какой из входящих ветвей размещать такую группу.

В текущей БД доступны граф, модификаторы и условия; данные `upgrades_to`/`upgrades` потребуют отдельного обогащения. Это предложение будущей работы, а не выполненное изменение бэкэнда.

Универсального проверенного признака, который однозначно определяет игровое семейство для всех 39 случаев, не найдено. Зато есть воспроизводимые признаки с разной силой свидетельства, а также конкретные контрпримеры к простым структурным правилам. Следующие решения фиксируются после обсуждения в [документе цепочек и сортировки](TECHNOLOGY_CHAINS_AND_SORTING_RU.md).

## Материалы и проверка

- `data/chain_analysis/audit_ambiguities.py` → `ambiguities.json`: все 39 случаев, кандидаты, поля, непосредственная обязательность и результаты девяти сравнений.
- `data/chain_analysis/audit_unlocks.py` → `unlock_evidence.json`: 83 прочитанных файла, их SHA-256, 1892 объекта, 60 положительных свидетельств, нераскрытые вставки и неразрешённые цели улучшений. Ошибок синтаксического разбора и дублей ключей в рассмотренных объектах не обнаружено.
- `data/chain_analysis/audit_path_cover.py` → `path_cover_experiment.json`: глобальный эксперимент и все допустимые родители каждого случая при том же максимуме продолжений.
- Корректность размера паросочетания сверена с независимым полным перебором вариантов на 80 малых случайных графах. Для полного графа 12 перестановок порядка обхода сохранили максимум и все заявленные вынужденные выборы.
- Проверка относится к базовым представлениям технологий. Ручные варианты и состояние конкретного государства не вычислялись.
- SHA-256 исходной БД: `a3ef07a166dee5b7be4a17608e20c6545a99321247802268939985b92689c858`.

Запуск исследовательских скриптов: Python из `data/.venv/Scripts/python.exe` с параметром `-B`; сначала `audit_ambiguities.py`, затем `audit_unlocks.py` и `audit_path_cover.py`. Это временные инструменты анализа в игнорируемом каталоге `data/`.

[English version](RESEARCH_AMBIGUOUS_CHAINS_EN.md).
