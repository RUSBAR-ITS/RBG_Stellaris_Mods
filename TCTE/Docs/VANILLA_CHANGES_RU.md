# Tass Cheat Tool Extender — затронутые ванильные файлы и функции

## Оглавление

- [Текущее состояние](#текущее-состояние)
- [Триггер модификации видов](#триггер-модификации-видов)
- [Влияние версии 0.0.1](#влияние-версии-001)
- [Список общих ключей](#список-общих-ключей)
- [Границы изменений](#границы-изменений)

## Текущее состояние

В версии 0.0.8 изменён один ванильный триггер — `can_remove_beneficial_genetic_traits`. Состав 54 общих ключей локализации сохранён. Новые варианты, события и ключи используют префикс `tcte_`; переопределения Tass Cheat Tool перечислены отдельно в [BASE_MOD_CHANGES_RU.md](BASE_MOD_CHANGES_RU.md). Меню ресурсов использует штатный `add_resource` и ссылки на существующие названия; ванильные определения ресурсов и их вместимость не изменяются.

Реализация 0.0.1 от 2026-11-14 по утверждённому [ТЗ](TZ_RU.md). В поставку включены все 54 общих ключа из таблицы. Изменяются русские подписи; игровые функции и эффекты не переопределяются. Физические файлы игры и Workshop не изменены.

В версии 0.0.2 состав общих ключей сохранён. Пять кнопок предтеч в локализации Tass теперь ссылаются на существующие `precursor.1.name`, `precursor.500.name`, `precursor.1000.name`, `precursor.1500.name` и `precursor.2000.name`. Эти ванильные ключи только используются, их определения не переопределяются.

Версия 0.0.8 не добавляет ванильных переопределений: меню послов использует собственную `tcte_tech_extra_envoys` и штатные `give_technology`, `while`, `envoys_add`. Ванильные технологии, класс посла и defines не меняются.

## Триггер модификации видов

В TCTE 0.0.7 файл `common/scripted_triggers/tcte_species_traits_triggers.txt` содержит только `can_remove_beneficial_genetic_traits`. Источник — `common/scripted_triggers/05_scripted_triggers_traits.txt` установленной Stellaris `v4.5.*`. Полная копия этого файла удалена из TCTE; остальные 49 определений загружаются из ванили. Физический файл игры не изменён.

Переопределение выполняется по ID с сохранением существующих вызовов. Имя файла TCTE сортируется после исходного имени; `replace_path` не используется. Блок нашего триггера сохранён побайтово из 0.0.6. [Проверка отдельного переопределения](../../TMP/TCTE/trigger_override_validation.json); загрузку движком проверяет пользователь в игре.

Сохранена проверка наличия `from`, то есть модифицирующего государства. Внутри этой области действует **исходное разрешение по традициям ИЛИ (игрок И `tech_gene_expressions` И `modifier_tass_extra_species_modding`)**. Новая ветка не применяется к ИИ. Отключение чита закрывает только дополнительный путь; обычное право от традиций сохраняется.

`can_remove_vocational_genetic_traits`, определения технологий, традиций и отдельных признаков не меняются. Новое условие действует только там, где вызывается общий триггер; другие ограничения признака сохраняются. ID триггера оставлен ванильным для существующих вызовов. [ТЗ](TZ_SPECIES_RU.md), [256 проверенных сочетаний](../../TMP/TCTE/species_modding_truth_table.json), [отчёт](../../TMP/TCTE/species_modding_validation.json).

## Влияние версии 0.0.1

Русская локализация воспроизводит 54 общих ключа из `localisation/replace/tass_replace_l_english.yml` Tass Cheat Tool версии `20261012`. Целевой файл: `TCTE/localisation/replace/tcte_tass_replace_l_russian.yml`.

У 32 ключей найдены явные определения в английской локализации установленной игры и в подготовленной русской ванильной базе. Остальные 22 в просмотренных ванильных файлах явно не определены; это не означает, что их имена используются исключительно модом Tass.

Затрагиваются подписи модификаторов во всех местах интерфейса, использующих эти ключи. Числовые эффекты и игровые функции не изменяются. Файлы-источники 32 пересечений:

- `main_3_l_english.yml` / `main_3_l_russian.yml`;
- `megacorp_l_english.yml` / `megacorp_l_russian.yml`;
- `modifiers_1_l_english.yml` / `modifiers_1_l_russian.yml`;
- `infernals_crisis_l_english.yml` / `infernals_crisis_l_russian.yml`.

Английские файлы находятся в `E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/`, русские источники таблицы — в `Localisation_Base/2-Prio_Vanilla/russian/`. При выборе терминов сохраняется приоритет Russian Localization Fix RE из ТЗ. Номера строк соответствуют исследованному снимку.

## Список общих ключей

| Общий ключ | Явный источник в русской ванильной базе |
| --- | --- |
| `mod_country_energy_produces_mult` | `megacorp_l_russian.yml:1969` |
| `mod_country_minerals_produces_mult` | `megacorp_l_russian.yml:1965` |
| `mod_country_food_produces_mult` | `megacorp_l_russian.yml:1961` |
| `mod_country_physics_research_produces_mult` | `megacorp_l_russian.yml:1975` |
| `mod_country_society_research_produces_mult` | `megacorp_l_russian.yml:1973` |
| `mod_country_engineering_research_produces_mult` | `megacorp_l_russian.yml:1971` |
| `mod_country_alloys_produces_mult` | `megacorp_l_russian.yml:1967` |
| `mod_country_consumer_goods_produces_mult` | `megacorp_l_russian.yml:1985` |
| `mod_country_trade_produces_mult` | `main_3_l_russian.yml:3832` |
| `mod_country_unity_produces_mult` | `megacorp_l_russian.yml:1963` |
| `mod_country_influence_produces_mult` | `megacorp_l_russian.yml:1983` |
| `mod_country_volatile_motes_produces_mult` | `megacorp_l_russian.yml:1979` |
| `mod_country_exotic_gases_produces_mult` | `megacorp_l_russian.yml:1981` |
| `mod_country_rare_crystals_produces_mult` | `megacorp_l_russian.yml:1977` |
| `mod_country_sr_living_metal_produces_mult` | Не найден |
| `mod_country_sr_dark_matter_produces_mult` | Не найден |
| `mod_country_sr_zro_produces_mult` | `modifiers_1_l_russian.yml:716` |
| `mod_country_nanites_produces_mult` | Не найден |
| `mod_country_minor_artifacts_produces_mult` | Не найден |
| `mod_country_astral_threads_produces_mult` | `megacorp_l_russian.yml:1987` |
| `mod_country_menace_produces_mult` | Не найден |
| `mod_country_advanced_logic_produces_mult` | Не найден |
| `mod_country_feral_insight_produces_mult` | Не найден |
| `mod_country_entropy_crystals_produces_mult` | Не найден |
| `mod_country_integrity_produces_mult` | Не найден |
| `mod_country_base_energy_produces_add` | `modifiers_1_l_russian.yml:674` |
| `mod_country_base_minerals_produces_add` | `modifiers_1_l_russian.yml:675` |
| `mod_country_base_food_produces_add` | `modifiers_1_l_russian.yml:676` |
| `mod_country_base_physics_research_produces_add` | Не найден |
| `mod_country_base_society_research_produces_add` | Не найден |
| `mod_country_base_engineering_research_produces_add` | Не найден |
| `mod_country_base_alloys_produces_add` | `modifiers_1_l_russian.yml:70` |
| `mod_country_base_consumer_goods_produces_add` | `modifiers_1_l_russian.yml:69` |
| `mod_country_base_trade_produces_add` | Не найден |
| `mod_country_base_unity_produces_add` | `modifiers_1_l_russian.yml:680` |
| `mod_country_base_influence_produces_add` | `modifiers_1_l_russian.yml:693` |
| `mod_country_base_volatile_motes_produces_add` | `modifiers_1_l_russian.yml:711` |
| `mod_country_base_exotic_gases_produces_add` | `modifiers_1_l_russian.yml:712` |
| `mod_country_base_rare_crystals_produces_add` | `modifiers_1_l_russian.yml:710` |
| `mod_country_base_sr_living_metal_produces_add` | `modifiers_1_l_russian.yml:713` |
| `mod_country_base_sr_dark_matter_produces_add` | `modifiers_1_l_russian.yml:714` |
| `mod_country_base_sr_zro_produces_add` | `modifiers_1_l_russian.yml:715` |
| `mod_country_base_nanites_produces_add` | `modifiers_1_l_russian.yml:71` |
| `mod_country_base_minor_artifacts_produces_add` | Не найден |
| `mod_country_base_astral_threads_produces_add` | `megacorp_l_russian.yml:1988` |
| `mod_country_base_menace_produces_add` | Не найден |
| `mod_country_base_advanced_logic_produces_add` | Не найден |
| `mod_country_base_feral_insight_produces_add` | Не найден |
| `mod_country_base_entropy_crystals_produces_add` | `infernals_crisis_l_russian.yml:12` |
| `mod_country_base_integrity_produces_add` | Не найден |
| `mod_fleet_command_limit_add` | Не найден |
| `mod_shipclass_research_station_build_speed_mult` | Не найден |
| `mod_shipclass_observation_station_build_speed_mult` | Не найден |
| `mod_shipclass_starbase_build_speed_mult` | Не найден |

## Границы изменений

Все 54 ключа являются переопределениями или дополнениями локализации общих модификаторов, а не новыми функциями TCTE. Для `mod_fleet_command_limit_add` неверная ссылка заменена на `$MOD_COMMAND_LIMIT_ADD$`; сам ключ `MOD_COMMAND_LIMIT_ADD` не переопределяется.

Остальные 1 612 исходных ключей Tass не пересекаются с явно определёнными ключами просмотренной ванильной локализации. Дополнительный `TASS_CHEAT_WORMHOLE` обслуживает уже существующий тип обходного пути базового мода и ссылается на `$BYPASS_TASS_CHEAT_WORMHOLE$`.

Физические файлы установленной игры не изменены. В 0.0.7 поставляется только переопределение указанного триггера; остальные определения его исходного файла не копируются в TCTE. Состав общих строк соответствует исходной поставке 0.0.1 и сохранён в 0.0.8. Переопределения Tass учтены в отдельном списке базового мода.

[English version](VANILLA_CHANGES_EN.md) · [История изменений](CHANGELOG_RU.md).
