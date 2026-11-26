# RB_LE — затронутые файлы и функции

## Оглавление

- [Решение и события](#решение-и-события)
- [Цель и навигация](#цель-и-навигация)
- [Сведения о лидере](#сведения-о-лидере)

## Решение и события

В версии 0.0.2 «Отдел Кадров» задаётся отдельным планетарным решением. Оно проверяет владельца колонии и открывает событие для державы игрока. Для всех экранов используется штатная иллюстрация `GFX_evt_galactic_senate` из `interface/eventpictures.gfx`. Значок решения — `decision_politics`. Меню работает на событиях Stellaris `v4.6.*` и поставляется в самом RB_LE. [Решение](../../RB_LE/mod/common/decisions/rb_le_personnel.txt) · [События](../../RB_LE/mod/events/rb_le_dossier_events.txt)

## Цель и навигация

Текущего правителя определяет `ruler`. Остальных служащих возвращает `every_owned_leader`, класс проверяет `leader_class`. При подготовке страницы за каждой кнопкой закрепляется объект лидера через `save_event_target_as`. Кнопка выводит имя через `GetName` и открывает дело этого же персонажа. При выходе удаляются временные переменные и флаг открытого реестра. [Подготовка страницы](../../RB_LE/mod/common/scripted_effects/rb_le_register.txt) · [Проверки и требования](REQUIREMENTS_0_0_2_RU.md)

## Сведения о лидере

С версии 0.0.5 событие вызывает условные строки на самом персонаже, например `[rb_le_selected_leader.rb_le_job_line]`. Проверка `has_background_job` и подстановка `[GetBackgroundJob]` получают одного лидера. Так ваниль вызывает `[Actor.GetInviteIdeologyExtra]` и читает `[GetName]` в выбранной строке. Для родного ковчега строка события использует сохранённое имя цели `[rb_le_home_colony.GetName]` по примеру `[replacement_leader.GetSubclass]`. Оба образца находятся в `localisation/english/forceofwill_l_english.yml` и `common/scripted_loc/16_scripted_loc_forceofwill.txt`.

В версии 0.0.4 досье читает `GetAge`, `GetYearsOfService`, `Species.GetName`, `Species.GetClass`, `GetBackgroundEthic`, `GetBackgroundPlanet`, `GetHomeWorldBiome`, `GetBackgroundJob`, `GetClass` и `GetSubclass`. Для родного ковчега используется имя объекта `background_colony`. Проверки `has_background_job`, `num_leader_traits` с фильтром `is_subclass` и ванильные проверки личных принципов определяют видимость строк. Для типа проверяются `is_robotic` и архетипы `BIOLOGICAL` и `LITHOID`. У прочих нероботических рас сохраняется подпись «Нероботический». [Условия вывода](../../RB_LE/mod/common/scripted_loc/rb_le_dossier.txt)

Значения `has_base_skill`, `has_total_skill` и `has_experience` берутся у выбранного персонажа. Порог опыта читается через `get_leader_exp_to_level` по образцу `common/script_values/09_script_values_forceofwill.txt`. Базовый предел в Stellaris 4.6.0 равен 10 по `NGameplay.LEADER_BASE_SKILL_CAP` и `LEADER_MAX_SKILL_CAP` в `common/defines/00_defines.txt`. Четыре числовых поля хранятся у владельца реестра до закрытия дела. [Подготовка данных](../../RB_LE/mod/common/scripted_effects/rb_le_dossier.txt) · [Порог опыта](../../RB_LE/mod/common/script_values/rb_le_dossier.txt)
