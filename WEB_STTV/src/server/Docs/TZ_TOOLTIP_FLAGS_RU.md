# ТЗ. Игровой смысл флагов в тултипах технологий

## Оглавление

- [Охват](#охват)
- [Государство и население](#государство-и-население)
- [Проекты и открытия](#проекты-и-открытия)
- [Обнаруженные ресурсы](#обнаруженные-ресурсы)
- [Политики](#политики)
- [Игнорируемые условия](#игнорируемые-условия)
- [Вывод и приёмка](#вывод-и-приёмка)

## Охват

В Stellaris Cygnus v4.5.4 (1b4f) сверены четыре раздела всех 679 базовых технологий из MongoDB после раскрытия скриптов. В `potential` и `weight_modifier` найдены 100 проверок 32 разных технических флагов у 85 технологий. Из них 28 проверок относятся к доступности, 72 — к весу. В `prerequisites` и `allow` таких проверок нет. Ещё у 12 технологий найдено 13 проверок трёх флагов политик. Итого 35 значений, 113 проверок, 97 технологий. Это инвентаризация условий, выводимых в карточке технологии.

Ниже приведены положительные формулировки и места в скриптах, которые объясняют их смысл. У 31 технического флага подтверждена установка. Единственный глобальный флаг — `l_cluster_opened`. Остальные 31 технический флаг относятся к государству. Флаги политик имеют отдельный тип и свой действующий источник подписей.

## Государство и население

| Флаг | Что означает в игре | Основание в скриптах |
|---|---|---|
| `has_market_access` | У государства есть доступ к галактическому рынку. | [on_action_events_2.txt:268](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_2.txt:268) · [galactic_community_events.txt:694](E:/SteamLibrary/steamapps/common/Stellaris/events/galactic_community_events.txt:694) |
| `first_spynetwork` | Государство игрока уже создавало агентурную сеть в другом обычном государстве. | [nemesis_espionage_events.txt:22](E:/SteamLibrary/steamapps/common/Stellaris/events/nemesis_espionage_events.txt:22) · [nemesis_espionage_events.txt:58](E:/SteamLibrary/steamapps/common/Stellaris/events/nemesis_espionage_events.txt:58) |
| `chosen_empire` | Это государство Избранных. | [special_system_initializers.txt:2704](E:/SteamLibrary/steamapps/common/Stellaris/common/solar_system_initializers/special_system_initializers.txt:2704) · [special_system_initializers.txt:2719](E:/SteamLibrary/steamapps/common/Stellaris/common/solar_system_initializers/special_system_initializers.txt:2719) |
| `synthetic_empire` | Это синтетическое государство. | [machine_age_situation_events_2.txt:649](E:/SteamLibrary/steamapps/common/Stellaris/events/machine_age_situation_events_2.txt:649) · [unique_system_events.txt:971](E:/SteamLibrary/steamapps/common/Stellaris/events/unique_system_events.txt:971) |
| `machine_subspecies` | При основании государства его дополнительный вид был механическим или машинным. | [species_subspecies.txt:17](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/game_start/species_subspecies.txt:17) · [species_subspecies.txt:28](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/game_start/species_subspecies.txt:28) |
| `non_lithoid_subspecies` | При создании государства для его дополнительного вида была предусмотрена пища. | [species_subspecies.txt:59](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/game_start/species_subspecies.txt:59) · [01_start_of_game_effects.txt:2263](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/01_start_of_game_effects.txt:2263) · [01_start_of_game_effects.txt:3057](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/01_start_of_game_effects.txt:3057) |
| `found_presapients` | Государству известны предразумные виды. | [uplifting_events.txt:202](E:/SteamLibrary/steamapps/common/Stellaris/events/uplifting_events.txt:202) · [game_start.txt:588](E:/SteamLibrary/steamapps/common/Stellaris/events/game_start.txt:588) · [00_policies.txt:4277](E:/SteamLibrary/steamapps/common/Stellaris/common/policies/00_policies.txt:4277) |
| `bio_cloning` | Государство выбрало клонирование как направление биологического развития. | [biogenesis_events.txt:3255](E:/SteamLibrary/steamapps/common/Stellaris/events/biogenesis_events.txt:3255) · [biogenesis_events.txt:3267](E:/SteamLibrary/steamapps/common/Stellaris/events/biogenesis_events.txt:3267) · [biogenesis_events.txt:3453](E:/SteamLibrary/steamapps/common/Stellaris/events/biogenesis_events.txt:3453) |
| `covenant_end_of_the_cycle` | Государство заключило договор с Завершителем цикла. | [shroud_shadows_scripted_effects.txt:2409](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/shroud_shadows_scripted_effects.txt:2409) · [shroud_shadows_scripted_effects.txt:2420](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/shroud_shadows_scripted_effects.txt:2420) · [utopia_shroud_events.txt:6466](E:/SteamLibrary/steamapps/common/Stellaris/events/utopia_shroud_events.txt:6466) |

`first_spynetwork` запоминает первую подходящую сеть. В событии проверяются `is_ai = no` и обычный тип государства-цели. `synthetic_empire` может появиться при образовании синтетического государства или во время оцифровки. `non_lithoid_subspecies` характеризует стартовую настройку дополнительного вида. В ней есть отдельные ветви для машин, литоидов и инферналов, а также особый случай `is_guided_sapience_empire`. Проверка сегодняшнего состава населения дала бы иной результат.

## Проекты и открытия

| Флаг | Что означает в игре | Основание в скриптах |
|---|---|---|
| `colossus_project` | Завершён проект «Колосс». | [apocalypse_events.txt:575](E:/SteamLibrary/steamapps/common/Stellaris/events/apocalypse_events.txt:575) · [apocalypse_events.txt:581](E:/SteamLibrary/steamapps/common/Stellaris/events/apocalypse_events.txt:581) |
| `can_build_star_eaters` | Государство получило возможность строить пожиратели звёзд. | [nemesis_crisis_endgame.txt:233](E:/SteamLibrary/steamapps/common/Stellaris/events/nemesis_crisis_endgame.txt:233) · [nemesis_crisis_endgame.txt:242](E:/SteamLibrary/steamapps/common/Stellaris/events/nemesis_crisis_endgame.txt:242) |
| `origin_shoulders_closure` | Государство дошло до развязки истории происхождения «На плечах гигантов». | [origin_events_2.txt:2686](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_2.txt:2686) · [origin_events_2.txt:2993](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_2.txt:2993) |
| `artifact_yuht_research_completed` | Завершено исследование «Секреты юутов». | [ancient_relics_arcsite_events_2.txt:6724](E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:6724) · [ancient_relics_arcsite_events_2.txt:6766](E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:6766) |
| `finish_shroud_forged_liberation_flag` | Ситуация «Выкованные Покровом» завершилась освобождением покроворождённых. | [03_origin_situations.txt:261](E:/SteamLibrary/steamapps/common/Stellaris/common/situations/03_origin_situations.txt:261) |
| `encountered_first_lgate` | Государство обнаружило свои первые L-врата. | [apocalypse_events.txt:92](E:/SteamLibrary/steamapps/common/Stellaris/events/apocalypse_events.txt:92) · [distant_stars_events_3.txt:2402](E:/SteamLibrary/steamapps/common/Stellaris/events/distant_stars_events_3.txt:2402) |
| `completed_lcluster_chain` | Государство собрало все сведения для открытия L-скопления. | [00_scripted_effects.txt:3268](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt:3268) · [00_scripted_effects.txt:3274](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt:3274) |
| `l_cluster_opened` | Доступ в L-скопление уже открыт. | [distant_stars_events_3.txt:1338](E:/SteamLibrary/steamapps/common/Stellaris/events/distant_stars_events_3.txt:1338) |
| `advanced_identity_creation` | Государство получило доступ к продвинутым методам создания синтетических личностей. | [machine_age_situation_events_2.txt:1164](E:/SteamLibrary/steamapps/common/Stellaris/events/machine_age_situation_events_2.txt:1164) · [machine_age_situation_events_2.txt:1199](E:/SteamLibrary/steamapps/common/Stellaris/events/machine_age_situation_events_2.txt:1199) · [origin_events_machine_age.txt:2100](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_machine_age.txt:2100) |
| `synth_queen_knowledge` | Государство получило от Сетаны знания для исследования «Мысль Сетаны». | [02_machine_age_effects.txt:3477](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/02_machine_age_effects.txt:3477) |
| `cosmogenesis_aborted` | Государство согласилось прекратить Космогенез по требованию угасшей империи материалистов. | [machine_age_crisis_events.txt:2617](E:/SteamLibrary/steamapps/common/Stellaris/events/machine_age_crisis_events.txt:2617) · [machine_age_crisis_events.txt:2623](E:/SteamLibrary/steamapps/common/Stellaris/events/machine_age_crisis_events.txt:2623) |
| `has_quantum_catapult_insight` | Совершено астральное действие «Получить знания о квантовых катапультах». | [astral_planes_actions.txt:69](E:/SteamLibrary/steamapps/common/Stellaris/common/astral_actions/astral_planes_actions.txt:69) |
| `starfire_cannon_unlocked` | Исход событий у родной звезды открыл исследование пушки звёздного огня. | [infernals_1_events.txt:1100](E:/SteamLibrary/steamapps/common/Stellaris/events/infernals_1_events.txt:1100) · [infernals_1_events.txt:1338](E:/SteamLibrary/steamapps/common/Stellaris/events/infernals_1_events.txt:1338) · [infernals_1_events.txt:5506](E:/SteamLibrary/steamapps/common/Stellaris/events/infernals_1_events.txt:5506) |
| `has_encountered_psionic_auras` | Государство уже сталкивалось с псионической аурой. | [psionic_auras_scripted_effects.txt:284](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/psionic_auras_scripted_effects.txt:284) · [00_auras.txt:989](E:/SteamLibrary/steamapps/common/Stellaris/common/patrons/psionic_auras/00_auras.txt:989) |
| `payback_researching_gene_clinics` | Во время кризиса здравоохранения государство увеличило финансирование медицинских исследований. | [origin_events_4.txt:3124](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_4.txt:3124) · [origin_events_4.txt:3136](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_4.txt:3136) |
| `tech_mine_rare_crystals_culling_boost` | Государство отправило на убой кристаллический организм. | [00_on_actions.txt:5494](E:/SteamLibrary/steamapps/common/Stellaris/common/on_actions/00_on_actions.txt:5494) · [origin_events_grand_archive.txt:7315](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_grand_archive.txt:7315) · [origin_events_grand_archive.txt:7323](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_grand_archive.txt:7323) |

У L-врат три независимых факта. Одна империя может обнаружить врата, другая — собрать сведения, а открытие L-скопления учитывается для всей галактики. У пушки звёздного огня одинаковый результат дают исход со сверхновой и варианты стабилизации звезды. Для бонуса к добыче редких кристаллов игра проверяет тип особи при событии убоя космической фауны.

## Обнаруженные ресурсы

| Флаг | Что означает в игре | Основание в скриптах |
|---|---|---|
| `astral_threads_found` | Найдены астральные нити. | [on_action_events_1.txt:8094](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:8094) · [origin_events_astral_planes.txt:23](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_astral_planes.txt:23) |
| `sr_living_metal_found` | Найден живой металл. | [on_action_events_1.txt:8084](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:8084) |
| `volatile_motes_found` | Найдена летучая пыль. | [on_action_events_1.txt:8054](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:8054) |
| `exotic_gases_found` | Найдены экзотические газы. | [on_action_events_1.txt:8044](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:8044) |
| `rare_crystals_found` | Найдены редкие кристаллы. | [on_action_events_1.txt:8034](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:8034) |
| `sr_dark_matter_found` | Найдена тёмная материя. | [on_action_events_1.txt:8074](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:8074) |

Флаг отмечает, что государство нашло ресурс. При происхождении `origin_riftworld` астральные нити считаются найденными уже на старте.

## Политики

| Флаг | Что означает в игре | Основание в скриптах |
|---|---|---|
| `ai_outlawed` | Искусственный интеллект объявлен вне закона. | [00_policies.txt:4016](E:/SteamLibrary/steamapps/common/Stellaris/common/policies/00_policies.txt:4016) |
| `robots_outlawed` | Использование рабочих-роботов запрещено. | [00_policies.txt:4189](E:/SteamLibrary/steamapps/common/Stellaris/common/policies/00_policies.txt:4189) |
| `slavery_allowed` | Рабство разрешено. | [00_policies.txt:4745](E:/SteamLibrary/steamapps/common/Stellaris/common/policies/00_policies.txt:4745) |

Здесь указано значение выбранного варианта. В интерфейсе сохраняется существующая подпись из `wiki.policies` и `wiki.localization`. В частности, флаг `robots_outlawed` устанавливает вариант `robot_pops_outlawed` политики `robot_pop_policy`.

## Игнорируемые условия

| Проверка | ID флага | Правило вывода RU/EN |
|---|---|---|
| `has_country_flag` | `crystal_armor_1_weight` | Скрыть условие. Оно единственное у прибавки +5, поэтому скрыть всю строку модификатора. Если раздел веса опустел, скрыть и его заголовок. |

`crystal_armor_1_weight` относится к технологии «Обшивка с внедрёнными кристаллами». Её базовый вес равен 0, а проверка флага прибавляет 5. В проверенных скриптах найдена проверка этого имени. Установку флага и достаточное для неё событие подтвердить не удалось. Аномалия `anomaly.6890` передаёт эту же технологию эффекту `add_tech_option_or_research_effect`, который выдаёт вариант исследования, прогресс или очки науки. Это отдельный путь получения. [Проверка веса](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2009) · [Аномалия](E:/SteamLibrary/steamapps/common/Stellaris/events/anomaly_events_4.txt:3293) · [Тело эффекта](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt:4904)

Проверена гипотеза о победе над кутхолоидом в v4.5.4. После гибели дикого кутхолоида `grand_archive.3025` может создать обломки. Научный корабль с учёным изучает их 90 дней. В `grand_archive.3026` две награды с равным весом: 1 000 минералов или 200 редких кристаллов. В этой цепочке установки флага обшивки нет. В ветке «Раздражённый кристалл» из аномалии появляется другое существо, кристаллический организм. На нём установлена биологическая версия обшивки. Обработчик уничтожения кристаллического флота `story.216` при активном бонусе за охоту выдаёт игроку 500 минералов. Прямая выдача варианта исследования обшивки подтверждена, в частности, в `story.205` и `story.207`. [Обломки кутхолоида](E:/SteamLibrary/steamapps/common/Stellaris/events/grand_archive_events.txt:3593) · [Завершение проекта](E:/SteamLibrary/steamapps/common/Stellaris/common/special_projects/04_projects_grand_archive.txt:168) · [Награды](E:/SteamLibrary/steamapps/common/Stellaris/events/grand_archive_events.txt:3637) · [Раздражённый кристалл](E:/SteamLibrary/steamapps/common/Stellaris/events/anomaly_events_4.txt:3256) · [Компонент организма](E:/SteamLibrary/steamapps/common/Stellaris/common/global_ship_designs/crystal_monster_designs.txt:940) · [Награда за охоту](E:/SteamLibrary/steamapps/common/Stellaris/events/story_events.txt:2630) · [Изучение](E:/SteamLibrary/steamapps/common/Stellaris/events/story_events.txt:2563) · [Умиротворение](E:/SteamLibrary/steamapps/common/Stellaris/events/story_events.txt:2621)

В снимке дерева v2.2.0 уже записаны базовый вес 0 и прибавка +1 за этот флаг. В архиве игровых скриптов ветки 2.2 за март 2019 года прибавка составляет +5. Среди 618 файлов `.txt` из `common` и `events` этого архива буквальное имя найдено только в проверке веса. Это подтверждает давность условия. Свидетельства, что победа над каким-либо существом когда-либо устанавливала этот флаг, пока нет. [Снимок v2.2.0](/D:/Repos/stellaris-tech-tree/leguin-2.2.0/anomalies.json:168) · [Историческое определение технологии](https://gitlab.com/stellaris/game/-/blob/a0c3fbc8f0678b9b6dd0931a036a335cfb8e34fa/game/common/technology/00_eng_tech.txt#L1631)

Исключение действует только при подготовке тултипа. Исходное условие и операция остаются в БД для последующего исследования.

## Вывод и приёмка

1. Сервер подбирает целую фразу по паре «вид проверки, ID флага» и выбранному языку. Достаточно дополнительных записей RU/EN в существующем проектном словаре локализации. Использовать игровые ключи для названий, когда они подходят по форме. Фронтенд выводит `text` существующим компонентом. Новая коллекция и поиск по событиям во время наведения не требуются.
2. Для отображаемых условий меняется только подпись предиката. Порядок, субъект, признаки государства или галактики, вложенные И/ИЛИ/НЕ/NAND/NOR и числовая операция сохраняются. Если отрицание уже следует из заголовка группы, положительную фразу внутри оставлять положительной. Текст не вычисляет текущее состояние партии.
3. Проверять список игнорируемых условий по точной паре «вид проверки, ID флага» до поиска подписи. Для нового неизвестного флага или отсутствующей строки выбранного языка сохранить видимое условие и операцию, дать нейтральную локализованную подпись и записать тип, ID, технологию и раздел в диагностику. Исключить подстановку сырого имени в пользовательскую фразу.
4. Перед публикацией сверить фактическое множество пар «тип, ID» с таблицами, найти новые значения и проверить обе локализации. У `tech_crystal_armor_1` в текущем наборе проверить отсутствие в тултипе технического ID, строки +5, заглушки и пустого заголовка раздела веса. На `tech_repeatable_lcluster_clue` проверить области действия и отрицания, на `tech_mine_rare_crystals` — отдельные условия обнаружения и убоя, на `tech_frontier_health` — последствие выбора из события. Сверить с текущим выводом флаги политик и прочие условия. Проверить новые подписи в API и браузере на RU и EN.

[Словарь условий](TZ_TOOLTIP_DICTIONARY_RU.md) · [English version](TZ_TOOLTIP_FLAGS_EN.md)
