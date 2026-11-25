# PCE 2.0.0 — ванильные файлы и функции

## Оглавление

- [Решение и прибавка](#решение-и-прибавка)
- [Выбор особенности](#выбор-особенности)
- [События обновления](#события-обновления)

## Решение и прибавка

Цель версии — Stellaris `v4.6.*`. PCE добавляет собственное решение, события и депозиты. Установленная ваниль использует `owned_planets_only` для решений ковчега. `carrier_event` принимает планету и корабль. Переменная, записанная из области колонии, хранится на её носителе. [Решения ковчегов](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/15_nomads_dlc_decisions.txt)

Множитель `mult` внутри `triggered_planet_modifier` повторяет механизм `d_cd_ancient_tunnels`. Ковчег также поддерживает местный модификатор `planet_max_districts_add` ванильного `d_compact_modules`. Эти два депозита принадлежат игре. PCE использует `every_deposit` и `remove_deposit = yes` для собственных экземпляров. [Древние тоннели](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/15_infernals_deposits.txt) · [Особенности ковчегов](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/17_nomads_deposits.txt)

## Выбор особенности

При обновлении игры сверить наборы `uses_district_set`, класс `pc_nanotech`, три модификатора особых колоний и условия гражданских моделей. Приоритеты рыцарей и паломников используют локальную специализацию ковчега или поселения. Проверка служителя гостеприимства учитывает завершение круиза. Точные условия и ссылки на районы, зоны и происхождения приведены в [ТЗ](REQUIREMENTS_RU.md). [Типы держав](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt) · [Служители гостеприимства](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/09_scripted_triggers_nomads.txt) · [Особые колонии и экуменополис](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/02_special_decisions.txt)

## События обновления

Для колонии или её носителя PCE подписывается на `on_planet_class_changed`, `on_terraforming_complete`, `on_decision_enacted`, `on_colony_transfer`, `on_colonized`, `on_zone_complete`, `on_district_demolished`, `on_arkship_encamped`, `on_arkship_mobile`. После внешнего преобразования повторная проверка на следующий игровой день учитывает ванильную очистку депозитов. [Игровые обработчики](E:/SteamLibrary/steamapps/common/Stellaris/common/on_actions/00_on_actions.txt)

Для державы используются `on_post_government_changed`, `on_modification_completion`, `on_policy_changed`. Обновляются только её колонии с положительным индексом. Дополнительная ежедневная проверка связана с конкретным установленным экземпляром PCE и учитывает сюжетные флаги, в том числе окончание круиза. После снятия прибавки дальнейшие проверки этого экземпляра прекращаются.
