# Stellaris Technological Tree View — стартовые технологии

## Оглавление

- [Область и критерий отбора](#область-и-критерий-отбора)
- [Итоги](#итоги)
- [Физика — 10](#физика--10)
- [Социология — 16](#социология--16)
- [Инженерия — 16](#инженерия--16)
- [Явное значение no](#явное-значение-no)
- [Значение для цепочек](#значение-для-цепочек)
- [Источники и проверка](#источники-и-проверка)

## Область и критерий отбора

Список от 2026-11-17 составлен по `data/stage10/database.json`: 679 базовых технологий. Отобраны объекты с явным верхнеуровневым `start_tech = yes`. Названия взяты из русской и английской локализации БД; варианты `technology_swap` не считаются отдельными технологиями.

`start_tech` — признак стартовой технологии; `starting_potential` задаёт дополнительные условия стартового получения. Также могут присутствовать общие условия `potential`. Здесь перечислены определения, а не вычислен стартовый набор конкретного государства. Дополнительная выдача технологий эффектами, происхождениями или событиями в эту выборку не входит.

В таблицах условия `starting_potential` приведены по исходному коду без комментариев и внешних скобок. Если условий несколько, они перечислены через точку с запятой. Прочерк означает отсутствие именно этого блока, а не безусловную доступность. Столбец `potential` отмечает наличие общего блока условий. Ссылка в ID ведёт на первую строку `start_tech` в установленной игре.

## Итоги

| Показатель | Количество |
| --- | ---: |
| Уникальные технологии с полем `start_tech` | 47 |
| Из них со значением `yes` | 42 |
| Из них со значением `no` | 5 |
| Вхождения самого поля, включая повторы | 50 |
| Стартовые технологии с `starting_potential` | 19 |
| Стартовые технологии с `tier = 0` | 38 |
| Стартовые технологии с `tier = 1` | 4 |
| Стартовые технологии с непустыми `prerequisites` | 11 |

У `tech_lasers_1`, `tech_mass_drivers_1` и `tech_wilderness_terraform` поле `start_tech = yes` повторено дважды. Каждая технология учитывается один раз; противоречия между значениями этого поля в выборке нет.

## Физика — 10

| Название | ID и источник | tier | starting_potential | potential |
| --- | --- | ---: | --- | --- |
| Научный метод | [tech_basic_science_lab_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:37) | 0 | `is_low_tech_start = no` | — |
| Ядерный реактор | [tech_fission_power](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:1491) | 0 | — | — |
| Путешествия через гиперпространство | [tech_hyper_drive_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:2558) | 0 | `is_eager_explorer_empire = no` | — |
| Красные лазеры | [tech_lasers_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_weapon_tech.txt:12) | 0 | — | — |
| Активные меры противодействия | [tech_pd_tracking_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_weapon_tech.txt:899) | 0 | — | — |
| Мощные конденсаторы | [tech_power_plant_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:2300) | 0 | — | — |
| Усилители реактора | [tech_reactor_boosters_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:1738) | 0 | — | — |
| Отражатели | [tech_shields_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:1789) | 0 | — | — |
| Исследование космоса | [tech_space_exploration](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:10) | 0 | — | — |
| Подпространственный двигатель | [tech_subspace_drive](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_first_contact_tech.txt:426) | 0 | `is_eager_explorer_empire = yes` | есть |

## Социология — 16

| Название | ID и источник | tier | starting_potential | potential |
| --- | --- | ---: | --- | --- |
| Медицинское обслуживание | [tech_basic_health](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:1256) | 0 | — | есть |
| Протокол освоения новых миров | [tech_colonization_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:1087) | 0 | `is_nomadic = no` | есть |
| Плодовые сады | [tech_critter_feeder](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_plantoids_tech.txt:8) | 0 | `has_origin = origin_fruitful` | есть |
| Синаптические сооружения | [tech_hive_node](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:5861) | 0 | — | есть |
| Голографические развлечения | [tech_holo_entertainment](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:5534) | 0 | — | есть |
| Гидропонное земледелие | [tech_hydroponics](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:543) | 0 | — | есть |
| Индустриальное сельское хозяйство | [tech_industrial_farming](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:177) | 0 | — | — |
| Межпланетная торговля | [tech_interplanetary_commerce](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:38) | 0 | — | есть |
| Мучители | [tech_maulers](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_biogenesis_tech.txt:13) | 1 | `is_low_tech_start = no` | есть |
| Планетарная оборона | [tech_planetary_defenses](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:7) | 0 | — | — |
| Унифицированное правительство | [tech_planetary_government](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:4610) | 0 | `is_low_tech_start = no` | — |
| Вектор-наводящаяся пушка | [tech_weaver_bio_anti_evasion_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_biogenesis_tech.txt:2038) | 1 | `is_low_tech_start = no` | есть |
| Энерговсплеск | [tech_weaver_bio_evasion_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_biogenesis_tech.txt:1266) | 1 | `is_low_tech_start = no` | есть |
| Ткачи | [tech_weavers](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_biogenesis_tech.txt:193) | 1 | `is_low_tech_start = no` | есть |
| Центры естества | [tech_wilderness_node](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:5909) | 0 | — | есть |
| Планетарное прорастание | [tech_wilderness_terraform](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_biogenesis_tech.txt:2637) | 0 | `is_wilderness_empire = yes` | есть |

## Инженерия — 16

| Название | ID и источник | tier | starting_potential | potential |
| --- | --- | ---: | --- | --- |
| Межпланетный экспедиционный корпус | [tech_assault_armies](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:1809) | 0 | — | — |
| Промышленная база | [tech_basic_industry](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2312) | 0 | — | — |
| Корветы | [tech_corvettes](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:26) | 0 | `is_low_tech_start = no`; `country_uses_bio_ships = no` | есть |
| Зенитная батарея | [tech_flak_batteries_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_weapon_tech.txt:620) | 0 | — | — |
| Ускорители масс | [tech_mass_drivers_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_weapon_tech.txt:12) | 0 | — | — |
| Механизированная добыча | [tech_mechanized_mining](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2331) | 0 | `is_nomadic = no` | есть |
| Ядерные ракеты | [tech_missiles_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_weapon_tech.txt:742) | 0 | — | есть |
| Стратегическая добыча | [tech_nomads_mechanized_mining](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_nomads_dlc_tech.txt:472) | 0 | `is_nomadic = yes` | есть |
| Нанокомпозитные материалы | [tech_ship_armor_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:1822) | 0 | — | — |
| Орбитальное преобразование энергии | [tech_solar_panel_network](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:9) | 0 | `is_nomadic = no` | есть |
| Космическое строительство | [tech_space_construction](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:3532) | 0 | — | — |
| Оборона дальнего космоса | [tech_space_defense_station_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2266) | 0 | `is_nomadic = no` | есть |
| Строительство космической базы | [tech_starbase_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:1130) | 0 | `is_nomadic = no` | есть |
| Звёздный порт | [tech_starbase_2](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:1157) | 0 | `is_nomadic = no` | есть |
| Химические двигатели | [tech_thrusters_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2078) | 0 | — | — |
| Маршрутные станции | [tech_waystation_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_nomads_dlc_tech.txt:491) | 0 | `is_nomadic = yes` | есть |

## Явное значение no

Эти пять технологий содержат поле, но не помечены стартовыми:

| Название | ID и источник | tier |
| --- | --- | ---: |
| Энтропическая рекурсия | [tech_akx_worm_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_horizonsignal_tech.txt:3) | 3 |
| Доктрина: Странное Кольцо | [tech_akx_worm_2](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_horizonsignal_tech.txt:32) | 3 |
| Теория омеги | [tech_akx_worm_3](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_horizonsignal_tech.txt:61) | 3 |
| Улучшенные седативы для криосна | [tech_enhanced_cryosleep_sedatives](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_strange_worlds_tech.txt:4) | 2 |
| Универсальный макрофаг | [tech_universal_marcophage](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_strange_worlds_tech.txt:17) | 3 |

## Значение для цепочек

Стартовые технологии первого уровня: `tech_maulers`, `tech_weavers`, `tech_weaver_bio_evasion_1`, `tech_weaver_bio_anti_evasion_1`.

У 11 стартовых технологий уже есть технологические предшественники. Например:

- `tech_starbase_1` требует `tech_space_construction`, а `tech_starbase_2` — `tech_starbase_1`; все три помечены стартовыми.
- `tech_reactor_boosters_1` требует стартовую `tech_fission_power`.
- `tech_weavers` требует стартовую `tech_maulers`.

Следовательно, `start_tech = yes` нельзя отождествлять с отсутствием входящих технологических связей или с `tier = 0`. Как использовать этот признак при построении цепочек, предстоит решить в [документе правил цепочек и сортировки](TECHNOLOGY_CHAINS_AND_SORTING_RU.md).

## Источники и проверка

- БД: `data/stage10/database.json`; SHA-256: `a3ef07a166dee5b7be4a17608e20c6545a99321247802268939985b92689c858`.
- Выборка с ID, названиями на двух языках, уровнями, предшественниками, условиями и координатами источников: `data/chain_analysis/starting_technologies.json`.
- Все 50 координат `start_tech` из БД сверены с прямым поиском по `E:/SteamLibrary/steamapps/common/Stellaris/common/technology/**/*.txt`; наборы совпали. Значения проверены на соответствующих строках исходников.
- Все 19 блоков `starting_potential` прочитаны в установленных файлах по координатам происхождения из БД. Условия не вычислялись для игрового государства.
- Исходная БД, код продукта и файлы игры не изменялись.

[English version](STARTING_TECHNOLOGIES_EN.md).
