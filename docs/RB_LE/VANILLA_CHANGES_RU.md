# RB_LE — затронутые файлы и функции

## Оглавление

- [Решение и события](#решение-и-события)
- [Цель и навигация](#цель-и-навигация)
- [Сведения о лидере](#сведения-о-лидере)
- [Редактирование лидера](#редактирование-лидера)

## Решение и события

В версии 0.0.2 «Отдел Кадров» задаётся отдельным планетарным решением. Оно проверяет владельца колонии и открывает событие для державы игрока. Для всех экранов используется штатная иллюстрация `GFX_evt_galactic_senate` из `interface/eventpictures.gfx`. Значок решения — `decision_politics`. Меню работает на событиях Stellaris `v4.6.*` и поставляется в самом RB_LE. [Решение](../../RB_LE/mod/common/decisions/rb_le_personnel.txt) · [События](../../RB_LE/mod/events/rb_le_dossier_events.txt)

## Цель и навигация

С версии 0.0.16 общий шаблон перелистывает реестры и каталог профессий через ванильные `check_variable`, `set_variable`, `change_variable` и `country_event`. Для «Назад» используется `BACK`, для русского «Выход» — `QUIT` и для английского Exit — `EXIT` из `main_1`. Русские подписи перелистывания хранятся в локализации RB_LE. [Шаблон перелистывания](../../RB_LE/mod/common/inline_scripts/rb_le/page_navigation.txt)

Текущего правителя определяет `ruler`. Остальных служащих возвращает `every_owned_leader`, класс проверяет `leader_class`. При подготовке страницы за каждой кнопкой закрепляется объект лидера через `save_event_target_as`. Кнопка выводит имя через `GetName` и открывает дело этого же персонажа. При выходе удаляются временные переменные и флаг открытого реестра. [Подготовка страницы](../../RB_LE/mod/common/scripted_effects/rb_le_register.txt) · [Проверки и требования](REQUIREMENTS_0_0_2_RU.md)

## Сведения о лидере

С версии 0.0.8 экран «Личные сведения» использует `diplomatic = yes` и передаёт в `picture_event_data.portrait` сохранённый объект лидера. Образец — ванильное событие `distar.158` в `events/distant_stars_events_1.txt`. Комната — `ethic_spaceship_room`. [Экран личных сведений](../../RB_LE/mod/events/rb_le_editor_events.txt)

Строка пола в 0.0.6 использует триггер лидера `gender` и ключи `GENDER`, `male`, `female`, `indeterminable` из локализации `main_3`. Например, в ванильном файле `events/astral_planes_events.txt` лидеру `NAME_Mercedes` явно задано значение `indeterminable`.

С версии 0.0.5 событие вызывает условные строки на самом персонаже, например `[rb_le_selected_leader.rb_le_job_line]`. Проверка `has_background_job` и подстановка `[GetBackgroundJob]` получают одного лидера. Так ваниль вызывает `[Actor.GetInviteIdeologyExtra]` и читает `[GetName]` в выбранной строке. Для родного ковчега строка события использует сохранённое имя цели `[rb_le_home_colony.GetName]` по примеру `[replacement_leader.GetSubclass]`. Оба образца находятся в `localisation/english/forceofwill_l_english.yml` и `common/scripted_loc/16_scripted_loc_forceofwill.txt`.

В версии 0.0.4 досье читает `GetAge`, `GetYearsOfService`, `Species.GetName`, `Species.GetClass`, `GetBackgroundEthic`, `GetBackgroundPlanet`, `GetHomeWorldBiome`, `GetBackgroundJob`, `GetClass` и `GetSubclass`. Для родного ковчега используется имя объекта `background_colony`. Проверки `has_background_job`, `num_leader_traits` с фильтром `is_subclass` и ванильные проверки личных принципов определяют видимость строк. Для типа проверяются `is_robotic` и архетипы `BIOLOGICAL` и `LITHOID`. У прочих нероботических рас сохраняется подпись «Нероботический». [Условия вывода](../../RB_LE/mod/common/scripted_loc/rb_le_dossier.txt)

Значения `has_base_skill`, `has_total_skill` и `has_experience` берутся у выбранного персонажа. Порог опыта читается через `get_leader_exp_to_level` по образцу `common/script_values/09_script_values_forceofwill.txt`. Базовый предел в Stellaris 4.6.0 равен 10 по `NGameplay.LEADER_BASE_SKILL_CAP` и `LEADER_MAX_SKILL_CAP` в `common/defines/00_defines.txt`. При выходе из отдела удаляются переменные открытого реестра. [Подготовка данных](../../RB_LE/mod/common/scripted_effects/rb_le_dossier.txt) · [Порог опыта](../../RB_LE/mod/common/script_values/rb_le_dossier.txt)

## Редактирование лидера

В 0.0.19 генератор сохраняет условие `has_branch_office = yes` ванильных зданий филиала перед обращением к `branch_office_owner` в их прибавках рабочих мест. Например, `building_private_security` в `common/buildings/14_branch_office_buildings.txt` проверяет наличие филиала в `potential`, а тип владельца — в `triggered_planet_modifier`. [Генератор каталога](../../Instruments/RB_LE_Background_Jobs/build.py)

Сборки 0.0.18 и 0.0.19 использовали ванильный эффект `log_error` для диагностики каталога прежних профессий. В 0.1.0 эти вызовы удалены. [Сбор списка профессий](../../RB_LE/mod/common/scripted_effects/rb_le_occupation_page.txt)

В 0.0.15 редактор читает прежнюю профессию через `has_background_job` и вызывает `change_background_job` у выбранного лидера. Названия вариантов берутся из ванильных ключей `job_<ID>`. Условие `has_ethic = ethic_gestalt_consciousness` проверяется у самого лидера. [События предыстории](../../RB_LE/mod/events/rb_le_background_events.txt)

В хозяйственных ветках `any_owned_colony` охватывает также ковчеги. Наличие мест проверяют `num_assigned_jobs` и `free_jobs_of_type`. Проверка `can_work_specific_job` выполняется у группы населения этой же колонии. Правила возможного строительства используют ванильные определения построек, районов, зон, владений и компонентов баз. Строки реестра указывают исходный файл и ветку для каждой прибавки. [Реестр источников Stellaris 4.6.0](BACKGROUND_JOB_VISIBILITY_SOURCES_4_6_0_RU.csv)

В 0.0.14 редактор вызывает `set_gender` у выбранного лидера по примеру `events/distant_stars_events_2.txt`. Экран считывает пол через триггер `gender` и использует готовые ключи локализации `GENDER`, `male`, `female` и `indeterminable`. В `gfx/portraits/portraits/07_portraits_human.txt` у современных людей для лидеров и правителей предусмотрены пять женских и пять мужских фенотипов. Бесполому лидеру доступны обе группы. [Команда смены пола](../../RB_LE/mod/common/inline_scripts/rb_le/gender_option.txt)

В 0.0.13 у каждого селектора украшения или одежды одна текстура по умолчанию. Такой селектор используется в ванильном `gfx/portraits/asset_selectors/aquatic_clothes_01.txt`. Образец и лидер получают одно полное определение портрета. При чтении через `species_portrait` игра может различить портреты, у которых изменена только одна деталь. [Генератор каталога](../../Instruments/RB_LE_Portraits/build.py)

С версии 0.0.12 применяется форма `change_leader_portrait = <ключ портрета>` в области видимости выбранного лидера. Ваниль использует её для смены облика Азарин в `events/paragon_events.txt`. Чтобы проверить запись, редактор сбрасывает портрет служебного вида, снова копирует облик с лидера через `change_species_characteristics` и сравнивает прочитанный ключ с показанным в предпросмотре. [Применение и проверка](../../RB_LE/mod/common/scripted_effects/rb_le_portrait.txt)

В Stellaris 4.6.0 инициализация вложенных скриптовых эффектов ограничена пятью проходами. Ваниль учитывает этот предел в `common/scripted_effects/shroud_shadows_scripted_effects.txt`. В версии 0.0.11 кнопки передают управление одному скрытому `country_event` (`rb_le.27`). Именно это событие обращается к каталогу и применяет выбранный образ. [Событие предпросмотра](../../RB_LE/mod/events/rb_le_portrait_events.txt)

Версия 0.0.10 читает фактический портрет выбранного персонажа через отдельный служебный вид по образцу `clones.1` в `events/clone_army_events.txt`. Окно показывает вид через `picture_event_data.portrait`, как в `origin.4015` в `events/origin_events_4.txt`. При принятии `change_leader_portrait` получает ссылку на вид, как в `events/origin_events_machine_age.txt`. У выбранного лидера сохраняются индексы одежды и украшения. За обновление изображения отвечает `refresh_portraits = character`. [Сеанс предпросмотра](../../RB_LE/mod/common/scripted_effects/rb_le_portrait.txt)

Генератор читает `common/portrait_categories`, `common/portrait_sets`, `gfx/portraits/portraits` и `gfx/portraits/asset_selectors`. Собственные определения в пространстве имён `rb_le_` ссылаются на ванильные модели и текстуры. Ванильные условия для обычной случайной генерации продолжают действовать у остальных лидеров. [Источники и воспроизведение каталога](../../Instruments/RB_LE_Portraits/README_RU.md)

В версии 0.0.9 для предпросмотра использовался временный персонаж, созданный через `create_saved_leader`. Событие показывает его по сохранённой ссылке. При завершении работы с образцом `remove_saved_leader` удаляет его. Такой жизненный цикл описан в `localisation/99_README_SAVED_LEADERS.txt` и используется в `events/origin_events_forceofwill.txt`. Для применения образец копируется в контрольный вид. Выбранный учёный получает его портрет через `change_leader_portrait` со ссылкой на вид по примеру `events/origin_events_machine_age.txt`. [Подготовка образца](../../RB_LE/mod/common/scripted_effects/rb_le_portrait.txt)

Прототип 0.0.8 использует `change_species_characteristics` с целью-лидером по образцу `clones.1` из `events/clone_army_events.txt`. Получателем служит специально созданный контрольный вид. Триггер `species_portrait` проверяет результат копирования. Ключи `human_female_01` и `human_female_02` взяты из `gfx/portraits/portraits/07_portraits_human.txt`. Применение использует `change_leader_portrait` по образцу событий Азарин в `events/paragon_events.txt`. [Чтение фенотипа](../../RB_LE/mod/common/scripted_effects/rb_le_portrait.txt) · [Тестовый сценарий](../../RB_LE/mod/events/rb_le_portrait_events.txt)

В 0.0.7 команда `change_background_ethic` применяется к выбранному персонажу по образцу `events/paragon_events_3.txt`. Текущий личный принцип проверяется ванильными триггерами `is_gestalt`, `is_egalitarian` и их аналогами для остальных принципов. Возраст читает `leader_age`, меняет `add_age`. Пример отрицательной прибавки есть в `events/astral_rifts_1_events.txt`. Нижние границы 16 и 0 задаёт редактор. [Условия действий](../../RB_LE/mod/common/scripted_triggers/rb_le_editor.txt)

Для опыта используется `add_experience`. В `common/council_agendas/00_council_agendas.txt` ваниль передаёт этой команде отрицательное скриптовое значение. Для снятия всего опыта редактор вычисляет отрицательное значение `has_experience` в момент применения. Понижение вызывает `set_skill` для выбранного базового уровня. [События](../../RB_LE/mod/events/rb_le_editor_events.txt) · [Скриптовые значения](../../RB_LE/mod/common/script_values/rb_le_editor.txt)
