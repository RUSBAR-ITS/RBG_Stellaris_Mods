# PDE 2.1.2 — ванильные файлы и функции

## Оглавление

- [Область изменений](#область-изменений)
- [Решение и депозиты](#решение-и-депозиты)
- [Состояние планеты](#состояние-планеты)

## Область изменений

PDE 2.1.2 использует собственные скрипты и ключи. Зависимости сверены с установленной Stellaris 4.6.0. Штатные решения, определения депозитов и события используются без переопределения ванильных файлов. Ниже указаны зависимости проекта, которые нужно сверять при смене версии игры. [ТЗ](TZ_RU.md)

## Решение и депозиты

| Механизм | Применение и источник |
| --- | --- |
| Текст эффекта решения | `custom_tooltip` задаёт текст карточки. В `hidden_effect` выполняются повторная проверка доступа и открытие редактора. [Ванильный пример](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/15_nomads_dlc_decisions.txt:251) |
| Карточка цели | Панель использует `GetClassName`, `GetName` и `solar_system`. Климат проверяется на целевом теле через `has_climate`, номера страниц берутся из переменных державы. [Классы небесных тел](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/00_planet_classes.txt) · [Пример подстановок](E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/cosmic_storms_l_english.yml:2244) |
| Иллюстрации пульта | Спрайты PDE используют ванильную маску `gfx/interface/situation_log/event_mask.dds` по образцу `GFX_evt_alien_planet`. [Регистрация в игре](E:/SteamLibrary/steamapps/common/Stellaris/interface/eventpictures.gfx:900) |
| Доступ к планетарным решениям | Штатные условия для своей колонии и незаселённого тела. PDE сверяет владельца системы (`space_owner`) и игрока-инициатора (`from`), а для колонии также проверяет `colony.owner`. Тип носителя определяет `carrier_is_type`. [Источник](E:/SteamLibrary/steamapps/common/Stellaris/common/game_rules/00_rules.txt:4779) |
| Добавление экземпляра | Для обычной особенности PDE вызывает `add_deposit`. Для блокера использует `add_blocker = { type = … blocked_deposit = none }`, чтобы игра не создавала случайную особенность под блокером. [Эффекты PDE](../../PDE/common/scripted_effects/cdpd_deposit_effects.txt) |
| Выбор одного экземпляра | На выбранном теле `random_deposit` и `is_deposit_type` ограничивают выбор экземплярами заданного ID. [Источник](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/01_start_of_game_effects.txt:3323) |
| Прямое удаление | Эффект `remove_deposit = yes` действует на выбранный экземпляр в области депозита. [Источник](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/07_overlord_decisions.txt:44) |
| Справочник ID и классов | Определения `common/deposits/`, классы и сценарии выдачи приведены для каждого ID. Игровое размещение вызывает эффект депозита на выбранном теле. [Справочник](DEPOSIT_CLASSIFICATION_RU.md) |
| Подсказка | Штатное окно определяет шрифт. Локализация использует `§R` и `§!` для красного предупреждения. [Источник](E:/SteamLibrary/steamapps/common/Stellaris/interface/core.gui:40) |
| Стабильность каньона с привидениями | Условие бонуса +10% к стабильности проверяет у владельца `is_spiritualist`. В подсказках добавления и удаления названия трёх подходящих принципов берутся из ключей `ethic_spiritualist`, `ethic_fanatic_spiritualist` и `ethic_absolute_spiritualist`. [Депозит](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/12_cosmic_storms_deposits.txt:53) · [Триггеры](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:1723) |
| Предварительный показ эффекта | Все кнопки добавления показывают применяемую команду `add_deposit` или `add_blocker` внутри `tooltip` на выбранном теле. [Шаблон меню](../../PDE/common/inline_scripts/cdpd/menu/cdpd_option_preview.txt) |
| Данные об эффектах | Источники выработки, содержания и модификаторов — `common/deposits/`, подключаемые скрипты должностей и блокеров, `scripted_variables` и `script_values`. Условия доступности зданий, районов и специализаций сверены с `common/buildings/`, `common/districts/`, `common/zones/` и `common/zone_slots/`. [Реестр депозитов](DEPOSIT_CLASSIFICATION_RU.md) |
| Статус колонии | Общее условие колонизируемого мира проверяет `is_colonizable = yes` или `is_colony = yes` через `cdpd_is_colonizable_or_colonized`. Для орбитальной залежи обе проверки должны дать отрицательный результат. Индивидуальные ограничения по классу тела и климату сохраняются. |
| Свойства в подсказках | Источники фиксированных чисел для равнин (+1), воронки (−1), титанических форм жизни (+8 и −1) и общего модификатора (+25%) перечислены в [таблице трёх депозитов](TZ_TOOLTIP_EFFECTS_RU.md#первая-проверка). Для воронки выработка энергии берётся из глобальной переменной `@ranger_small_production`; штрафы к выработке от должностей (−10%), росту основного вида (−10%) и содержанию поселений (+15%) заданы в подключаемом скрипте. [Застава](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/01_scripted_triggers_jobs.txt:434) · [Переменная](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_variables/00_scripted_variables.txt:488) · [Штрафы](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/deposits/environmental_architects_natural_blocker_modifier.txt) · [Группа гражданских моделей](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:5337) |

## Состояние планеты

В снимке 4.5.4 у 58 определений есть `on_cleared`. Для прямого удаления проверяются отдельно изменения состояния экземпляра и награды ванильной расчистки. В таблице указаны обязательная пара и переменные, найденные при проверке обработчиков. [Снимок определений](../../TMP/PDE/v4.5.4/deposits.json)

| Состояние | Связь с ванильным кодом |
| --- | --- |
| `d_titanic_life_blocker` / `titanic_life` | На старте ваниль ставит депозит по наличию модификатора. У самого депозита и модификатора отдельные бонусы. Событие происхождения также может отдельно выдать модификатор. PDE запоминает независимый модификатор, присутствовавший до добавления первого экземпляра. Если событие `grand_archive.1015` повторно выдаёт уже действующий модификатор, оно не записывает источник на планете. В этом случае удаление последнего экземпляра может снять и эту выдачу. [Установка пары](E:/SteamLibrary/steamapps/common/Stellaris/events/colony_events_3.txt:909) · [Депозит](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:879) · [Модификатор](E:/SteamLibrary/steamapps/common/Stellaris/common/static_modifiers/00_static_modifiers.txt:500) · [Отдельная выдача](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_grand_archive.txt:608) |
| `seed_bomb_blockers` | Бомбардировка увеличивает переменную и размещает грибной или растительный блокер. Обе расчистки уменьшают одну переменную и отдельно обрабатывают награды. [Выдача](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_5.txt:145) · [Грибной](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:1821) · [Растительный](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:1938) |
| `seismic_bombing_var` | Сейсмическая бомбардировка увеличивает переменную и добавляет кратер. При расчистке кратера ваниль вычитает единицу. [Выдача](E:/SteamLibrary/steamapps/common/Stellaris/events/infernals_1_events.txt:200) · [Расчистка](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/15_infernals_deposits.txt:192) |
| `pyrolatry_var` | Решение увеличивает переменную и выбирает один из пяти блокеров. Пять обработчиков расчистки вычитают по единице. При терраформировании отдельное событие может сбросить переменную. [Пять типов](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/14_infernal_decisions.txt:35) · [Определения блокеров](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/15_infernals_deposits.txt:208) · [Сброс](E:/SteamLibrary/steamapps/common/Stellaris/events/infernals_1_events.txt:6096) |
| `cd_pods_var` | При обычной расчистке стазисных капсул эта переменная продвигает отдельную особенность древних тоннелей. Прямое удаление капсул сохраняет её значение. [Капсулы и тоннели](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/15_infernals_deposits.txt:96) |
