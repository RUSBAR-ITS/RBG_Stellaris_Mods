# RUS_FIX_FIX — учёт затронутых файлов и функций

## Оглавление

- [Снимок 4.6.0](#снимок-460)
- [Участки совместимости](#участки-совместимости)

## Снимок 4.6.0

[Полный перечень 285 файлов](../../TMP/RUS_FIX_FIX/files.json) содержит относительные пути, размер, результат сравнения с Workshop, наличие одноимённого файла в ванили и UIOD. Для 254 файлов путь совпадает с ванильным. Для 33 архивов DLC проверены пересечения с этими путями и наличие английских и русских файлов локализации. Рабочие результаты отражают входные файлы до правок. На момент аудита игровая поставка локальной копии соответствует авторской версии 4.5.4 с пользовательским манифестом.

## Участки совместимости

С версии `4.5.15` мод замещает четыре файла в `prescripted_countries/`. При обновлении игры сверять **все определения** в каждом файле, включая соседние державы.

| Файл ванили | Авторская правка |
| --- | --- |
| `00_top_countries.txt` | `plantoid_humans.adjective` |
| `88_astral_planes_prescripted_countries.txt` | `certeran_covenant.ruler.ruler_title_female` |
| `89_first_contact_prescripted_countries.txt` | `resistance.ruler.ruler_title_female` |
| `90_toxoids_prescripted_countries.txt` | `knights.ruler.ruler_title_female` |

Вспомогательный `bureaucrat_rinfix` сверять с самостоятельной ванильной должностью `culture_worker` в `common/pop_jobs/02_specialist_jobs.txt`. Ветку дикого сознания в `GetResearcherPlural_rinfix` сверять с условием `is_wilderness_empire` и падежными формами `evosymbiont_plural_rinfix_cases`. [Проверенные поля, ветки и локализация](../../TMP/RUS_FIX_FIX/empires_jobs_4.5.15.json).

В `4.5.13` изменены пять русских файлов локализации: `scripted_loc_l_russian.yml`, `apocalypse_l_russian.yml`, `wilderness_l_russian.yml`, `strange_worlds_l_russian.yml` и `nemesis_content_l_russian.yml`. Сверены `GetPlanetMoon_RULOC`, `GetSabotagedStarbaseTitle`, определения договоров в `common/agreement_presets/`, постройка `ring_feeder` и выбор флага в `espionage_event_effects.txt`. Для биографий сопоставлены ветки `GetJob_gender_lower_FR` и авторской `background_job_rinfix`. [Доказательства по ключам](../../TMP/RUS_FIX_FIX/older_forms_review.json).

В `4.5.12` добавления затронули 33 файла в `localisation/russian/`. Правки прежних строк дополнительно затронули `toxoids_l_russian.yml`, всего 34 файла. Сопоставлены имена категорий в `common/pop_categories/00_social_classes.txt` и `02_other_categories.txt`, условие `is_warmongers_empire`, функции выбора текста предтеч, лидеров и восстаний. Условия поиска системы предтеч сверены с `has_accessible_precursor_system` и вызовами из `common/artifact_actions/artifact_actions.txt`. Для ремонта проверены `ship_orbit_repair`, `station_self_repair` в `common/static_modifiers/02_static_modifiers.txt` и параметры времени и скорости в `common/defines/00_defines.txt`. Служебные форматы имён сверены с ванильной локализацией. [Все пути и ключи](../../TMP/RUS_FIX_FIX/remaining_46_review.json) · [Итоговые строки и проверенные источники](../../TMP/RUS_FIX_FIX/remaining_46_result.json).

В версии `4.5.11` изменены шесть файлов в `localisation/russian/` с именами `main_2_l_russian.yml`, `modifiers_1_l_russian.yml`, `paragon_2_l_russian.yml`, `ancient_relics_l_russian.yml`, `leaders_l_russian.yml` и `triggers_effects_l_russian.yml`. Название и описание черты выбирают ванильные функции `triggered_gifted_name` и `triggered_gifted_desc` из `common/scripted_loc/08_scripted_loc_paragon.txt`. Выбор подзаголовка делегата задаёт `GetDelegateSubclassSubtitle` из `common/scripted_loc/16_scripted_loc_forceofwill.txt`. Эффекты губернатора сверены с `skill_official_colony_governor` в `common/static_modifiers/00_static_modifiers.txt` и двумя переменными в `common/scripted_variables/00_scripted_variables.txt`. [Ключи, ветки и источники](../../TMP/RUS_FIX_FIX/leaders_46.json).

В `4.5.10` добавлены ключи в четыре файла `localisation/russian/`. Требования к принципам находятся в `main_2_l_russian.yml`, привлекательность — в `main_1_l_russian.yml` и `modifiers_1_l_russian.yml`, условия по идеологии населения — в `triggers_effects_l_russian.yml`. Степени принципов сверены с `common/scripted_triggers/00_scripted_triggers.txt`, условия правительств — с `common/governments/civics/00_civics.txt` и `common/governments/authorities/00_authorities.txt`. Ванильные примеры количества и доли населения используют `pop_ideology_amount` и `pop_ideology_percentage`. [Ключи, пути и строки источников](../../TMP/RUS_FIX_FIX/ethics_ideology_46.json).

В `4.5.9` обновлён `localisation/russian/astral_rifts_3_l_russian.yml`. Условия веток сведены с `events/astral_rifts_3_events.txt`, где игра выбирает обычные описания, реплики «Потерянных создателей» и 19 вариантов описания передачи технологии. Для сцены 3055 сверены функции `GetResearchers` из `common/scripted_loc/00_scripted_loc.txt` и `GetSkinType` из `common/scripted_loc/09_scripted_loc_astral_planes.txt`, а также падежные формы покровов тела в авторском `astral_planes_l_russian.yml`. [Список затронутых ключей](../../TMP/RUS_FIX_FIX/astral_rifts_4.5.9.json).

В `4.5.8` дополнены `localisation/russian/economic_modifiers_l_russian.yml` и `localisation/russian/megacorp_l_russian.yml`. Источники двух групп подписей — категории `planet_purge_jobs` в `common/economic_categories/01_job_categories.txt` и `ship_cultural_envoy` в `common/economic_categories/00_common_categories.txt`. Ванильная функция `GetCulturalEnvoyNamePlural` в `common/scripted_loc/16_scripted_loc_forceofwill.txt` определяет отображаемое название кораблей. [Проверка всех 205 строк](../../TMP/RUS_FIX_FIX/economic_modifiers_46.json).

В версии `4.5.7` добавлено по одному ключу в `random_names/pop_faction_formats_l_russian.yml`, `wilderness_l_russian.yml` и `paragon_2_l_russian.yml` внутри `localisation/russian/`. Для чиновников ваниль генерирует модификатор по категории `leader_officials`. Генератор фракции у автора использует `{interlink}`, а новая строка формата разрешается в то же имя. Для лесов-садов обе ванильные локализации содержат ключ `…_uncapped_max`; его отдельный вывод в интерфейсе пока не подтверждён.

В версии `4.5.6` добавлены строки в семь файлов `localisation/russian/*_l_russian.yml` со следующими основами имён: `civic_and_origin_concepts`, `federations`, `federations_anniversary`, `main_1`, `megacorp`, `modifiers_1`, `nemesis_intel`. Для каждой строки совпадают ссылки в английском и русском файлах Stellaris 4.6.0. [Пути, ключи и итоговый текст](../../TMP/RUS_FIX_FIX/aliases_4.5.6.json).

В локальной версии `4.5.5` изменён `localisation/russian/utopia_ascension_l_russian.yml`. Восстановлены ванильные ключи `triggered_opinion_cyborgs_absolute` и `triggered_opinion_synthetics_absolute` для модификаторов из `common/opinion_modifiers/00_opinion_modifiers.txt`.

| Область | Затронутые файлы и функции |
| --- | --- |
| Локализация | 242 файла: 233 в `localisation/russian/` и 9 в `localisation/replace/`. Прочитаны 942 файла четырёх наборов источников (EN/RU 4.6, русский снимок и авторские строки). Парсер прочитал все записи. В исходной русской локализации игры у 14 ключей есть несовпадающие определения; для таких случаев нужен контекст файла. |
| Интерфейс | Все 19 авторских `.gui` совпадают по путям с ванилью и UIOD; вместе с двумя таблицами `.gfx` все 21 отличаются от ванили побайтово. Оба варианта 21 файла разобраны парсером. Перечень имён виджетов фиксирует структурные различия; одинаковые имена не гарантируют совпадение привязок и размеров. [Сравнение окон](../../TMP/RUS_FIX_FIX/interface.json). |
| Должности и категории | В `common/pop_jobs/02_specialist_jobs.txt` должность `culture_worker` имеет собственное определение. У автора 73 определения вспомогательных должностей и четыре категории. Из проверенных вызовов вида «имя = yes/no» в файле должностей 87 имён найдены среди ванильных scripted triggers. Из оставшихся два — встроенный `always` и отсутствующий `bureaucrat_is_culture_worker`. |
| Склонение, имена, фракции | В двух файлах `common/scripted_loc/` проверены явные ссылки `localization_key` и `default`: 753 различных ключа в файле биографий, 158 в общем файле. Найдена одна опечатка с лишним начальным подчёркиванием. Для генераторов имён держав и фракций все 661 и 168 различных частей соответственно найдены в действующей русской локализации. [Генераторы имён](../../TMP/RUS_FIX_FIX/name_generators.json). |
| Готовые державы | Точки сравнения — `prescripted_countries/00_top_countries.txt`, `88_astral_planes_prescripted_countries.txt`, `89_first_contact_prescripted_countries.txt`, `90_toxoids_prescripted_countries.txt` и `default.txt`. Проверять `florin` как отдельный авторский шаблон. Для четырёх скрытых держав есть подтверждение в журнале пользователя. |
| Шрифты и графика | Одна декларация шрифта и 10 файлов в `gfx/`: OrbitronCYR, два комплекта 3A, четыре однопиксельных значка категорий и логотип. Ссылка OrbitronCYR разрешается. У атласов 3A размер 512 × 512. В описании medium записано имя PNG при поставляемом DDS; у small отсутствует строка page. Видимый результат проверяется в движке. |
| Манифест и изображение | Собственное имя локального мода. `thumbnail.png` побайтово совпадает с авторским. |

[Проверки скриптов и ресурсов](../../TMP/RUS_FIX_FIX/compatibility_checks.json) · [Индекс определений](../../TMP/RUS_FIX_FIX/scripts.json) · [Проект ТЗ](TZ_COMPAT_46_RU.md).
