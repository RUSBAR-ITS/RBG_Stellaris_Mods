# Общий список задач RBG_Stellaris_Mods

## Оглавление

- [VANILLA-001 — передача CLASS в шаблоны признаков](#vanilla-001--передача-class-в-шаблоны-признаков)
- [VANILLA-002 — параметр RELIC в наградах Великого архива](#vanilla-002--параметр-relic-в-наградах-великого-архива)

## VANILLA-001 — передача CLASS в шаблоны признаков

- [ ] Подготовить и согласовать исправление передачи `CLASS` по цепочкам inline-вставок признаков лидеров.

Статус: отложено, реализация не начата. Найдено при аудите установленной игры средствами WEB_STTV, 2026-11-15. Затронуты 14 файлов `common/traits/`: 10 останавливаются в `trait/icon_element/council_no.txt`, ещё 4 — в `trait/icon.txt`.

Подтверждённые примеры:

- Вызов `trait/icon_negative` в [00_admiral_traits.txt:1836](/E:/SteamLibrary/steamapps/common/Stellaris/common/traits/00_admiral_traits.txt:1836) передаёт `ICON`, `COUNCIL`, `TIER`. Вложенный [council_no.txt:1](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/trait/icon_element/council_no.txt:1) использует `$CLASS$`, которого нет в этой цепочке.
- Вызов `trait/icon` в [06_distant_stars_traits.txt:8](/E:/SteamLibrary/steamapps/common/Stellaris/common/traits/06_distant_stars_traits.txt:8) тоже не передаёт `CLASS`, используемый [шаблоном:4](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/trait/icon.txt:4).

При подготовке исправления определить корректное значение для каждого случая, включая признаки нескольких классов лидеров; проверить передачу аргумента во вложенные вызовы. Не подставлять произвольный класс ради прохождения парсера. Способ поставки исправления определить в отдельном ТЗ; установленная игра остаётся доступной только для чтения.

Проверки будущего исправления: все 14 файлов раскрываются без ошибок `CLASS`; отображение иконок и подписей признаков проверяет пользователь в игре. Отсутствие аргумента подтверждено по коду; фактическое поведение движка при таком пропуске отдельно не проверялось.

## VANILLA-002 — параметр RELIC в наградах Великого архива

- [ ] Проверить предполагаемую опечатку `$RELIC$` и подготовить согласованное исправление шаблона награды.

Статус: отложено, реализация не начата. Ошибка затрагивает цепочки из `events/grand_archive_events.txt` и `events/leviathans_events_1.txt`.

В [stage_3_reward_option.txt:15](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/grand_archive/collection/stage_3_reward_option.txt:15) используется `gave_relic_$RELIC$`, но [вызывающий шаблон:1](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/grand_archive/collection/stage_3_reward_options_by_category.txt:1) передаёт `SELECTED_RELIC` и `OTHER_RELIC_1`–`OTHER_RELIC_4`. `RELIC` не передан. Остальные проверки и выдача выбранной реликвии используют `SELECTED_RELIC`.

Предполагаемое исправление — `$RELIC$` → `$SELECTED_RELIC$`; до реализации подтвердить назначение проверки по всему шаблону и его вызовам. Исправление оформить отдельно, без изменения установленной игры.

Проверки будущего исправления: обе цепочки событий раскрываются без ошибки `RELIC`; пользователь проверяет доступность награды, выдачу выбранной реликвии и защиту от повторной выдачи в игре.
