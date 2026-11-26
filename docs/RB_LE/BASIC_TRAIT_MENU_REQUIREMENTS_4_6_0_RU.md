# RB_LE — условия добавления базовых черт

## Оглавление

- [Как читать таблицы](#как-читать-таблицы)
- [Последовательность рангов](#последовательность-рангов)
- [Уровневые черты](#уровневые-черты)
- [Черты резерва лидеров](#черты-резерва-лидеров)
- [Только для стартового правителя](#только-для-стартового-правителя)
- [Черты вида и возвышения](#черты-вида-и-возвышения)
  - [Генетика и клонирование](#генетика-и-клонирование)
  - [Кибернетика](#кибернетика)
  - [Синтетика и виртуальность](#синтетика-и-виртуальность)
  - [Псионика](#псионика)
- [Черты происхождений](#черты-происхождений)
  - [Под единой властью](#под-единой-властью)
  - [Страх темноты](#страх-темноты)
  - [Золотое поколение](#золотое-поколение)
  - [Армия клонов](#армия-клонов)
  - [Охотники за бурями](#охотники-за-бурями)
  - [Отпрыски](#отпрыски)
  - [Полный сброс](#полный-сброс)
  - [Кибернетический культ](#кибернетический-культ)
  - [Синтетическая репродуктивность](#синтетическая-репродуктивность)
  - [Покроворождённые](#покроворождённые)
- [Черты державы и должности](#черты-державы-и-должности)
  - [Правители и наследники](#правители-и-наследники)
  - [Специализированные вассалы](#специализированные-вассалы)
  - [Культурные посланники](#культурные-посланники)
  - [Паладины](#паладины)
- [Событийные черты](#событийные-черты)
  - [Покров](#покров)
  - [Аномалии и исследования](#аномалии-и-исследования)
  - [Астральные разломы](#астральные-разломы)
  - [Левиафаны](#левиафаны)
  - [Приключения ковчегов](#приключения-ковчегов)
  - [Прочие сюжетные цепочки](#прочие-сюжетные-цепочки)
- [Черты особых лидеров](#черты-особых-лидеров)
  - [Уникальные персонажи](#уникальные-персонажи)
  - [Анклавы и караванщики](#анклавы-и-караванщики)
  - [Кризисы и особые фракции](#кризисы-и-особые-фракции)
- [Прямые оппозиты](#прямые-оппозиты)
- [Особые случаи и источники](#особые-случаи-и-источники)

## Как читать таблицы

Ветка «Добавить черты → Базовые черты» для Stellaris 4.6.0 содержит 254 игровых ID в восьми разделах. Каждая строка описывает одну кнопку для выбранного лидера. В заголовке раздела указано число кнопок до фильтрации.

Кнопка доступна, когда выполнены условия класса, лидера, текущей державы-владельца и ранга. У лидера должны отсутствовать как сам выдаваемый ID, так и все черты из его прямого списка `opposites`. Знак «+» соединяет обязательные условия. Прочерк означает отсутствие дополнительного фильтра в этой колонке. «Все три» охватывает командира, чиновника и учёного. Для проверки вида используется вид самого лидера. Независимые машины и машинный разум различаются по державе.

Названия папок указывают на ванильный способ получения. Игрок может выдать черту действующему лидеру, даже если её обычный источник — резерв, старт партии или событие. В меню не требуется воспроизводить розыгрыш, проходить цепочку или выполнять её экономические условия. Для событийных вариантов в таблицу включены проверки адресата. Подстановка имени, описание и условия действия бонуса сами по себе видимость кнопки не меняют.

После выдачи или смены лидера либо его этики меню пересчитывает доступность. В нём остаются только папки, у которых на любой глубине есть доступное действие. Разбиение на страницы выполняется после этой проверки.

## Последовательность рангов

В ванильных определениях базовых черт 32 цепочки с 36 переходами через `replace_traits`. У 28 цепочек два ранга, у четырёх — три. Все ранги остаются в папке первого.

1. Если у лидера ещё нет ни одного ранга цепочки, видна только кнопка I, при условии что подходят остальные фильтры.
2. В колонке «Ранг» стрелка указывает на точный ID, который требуется иметь сейчас. Выдача следующего ранга заменяет этот ID. Пропустить ранг или добавить младший поверх старшего нельзя.
3. На верхнем ранге все кнопки этой цепочки скрыты. Условия класса, лидера и державы берутся из строки выдаваемого ранга.

Пример. У «Буканьера» последовательность I → II → III целиком находится в «Только для стартового правителя». У «Одарённого» последовательность I → II целиком находится в «Чертах резерва лидеров». После получения I повышение доступно в той же папке даже у уже нанятого лидера.

Цифра на значке или в ID сама по себе не создаёт повышение. «Изменённый метаболизм» имеет значок III и выдаётся самостоятельно. У Азарин число ядер убывает с трёх до одного. Варианты боевых имплантов в «Полном сбросе» меняет ситуация. Строки этих двух семейств помечены как сюжетные состояния, а варианты озарения Покровом с суффиксами 01 и 02 — самостоятельные исходы.

## Уровневые черты

93 ID.

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Гибкость<br>`leader_trait_adaptable` [↔](#прямые-оппозиты) | все три | — | — | — |
| Агрессивность<br>`leader_trait_aggressive` [↔](#прямые-оппозиты) | командир | — | — | — |
| Археолог<br>`leader_trait_archaeologist` | учёный | — | — | I · начало |
| Археолог II<br>`leader_trait_archaeologist_2` | учёный | — | — | II ← `leader_trait_archaeologist` |
| Увлечение архитектурой<br>`leader_trait_architectural_interest` [↔](#прямые-оппозиты) | чиновник, учёный | — | нет · кризисная фракция | — |
| Объединитель<br>`leader_trait_bureaucrat` | все три | — | нет · кризисная фракция | — |
| Беспощадность<br>`leader_trait_butcher` [↔](#прямые-оппозиты) | командир | — | нет · кризисная фракция | — |
| Энергетический магнат<br>`leader_trait_capitalist` [↔](#прямые-оппозиты) | все три | — | нет · кризисная фракция + нет · дикое сознание | I · начало |
| Энергетический магнат II<br>`leader_trait_capitalist_2` | все три | — | — | II ← `leader_trait_capitalist` |
| Беспечность<br>`leader_trait_carefree` [↔](#прямые-оппозиты) | учёный | — | — | I · начало |
| Беспечность II<br>`leader_trait_carefree_2` [↔](#прямые-оппозиты) | учёный | — | — | II ← `leader_trait_carefree` |
| Осторожность<br>`leader_trait_cautious` [↔](#прямые-оппозиты) | командир | — | — | — |
| Специальный ИИ-помощник<br>`leader_trait_custom_AI_assistant` [↔](#прямые-оппозиты) | учёный | — | — | — |
| Инженер обороны<br>`leader_trait_defence_engineer` | командир | — | нет · кочевая держава | — |
| Инженер<br>`leader_trait_engineer` | командир, учёный | — | — | — |
| Вербовщик<br>`leader_trait_enlister` | командир | — | нет · кризисная фракция | — |
| Предприниматель<br>`leader_trait_entrepreneur` [↔](#прямые-оппозиты) | все три | — | нет · кризисная фракция | I · начало |
| Предприниматель II<br>`leader_trait_entrepreneur_2` | все три | — | — | II ← `leader_trait_entrepreneur` |
| Инженер-эколог<br>`leader_trait_environmental_engineer` | все три | — | нет · кризисная фракция + нет · кочевая держава | — |
| Флотский логист<br>`leader_trait_fleet_logistician` | командир | — | — | — |
| Организатор флота<br>`leader_trait_fleet_organizer` [↔](#прямые-оппозиты) | командир | — | — | I · начало |
| Организатор флота II<br>`leader_trait_fleet_organizer_2` [↔](#прямые-оппозиты) | командир | — | — | II ← `leader_trait_fleet_organizer` |
| Фермер-поселенец<br>`leader_trait_homesteader` [↔](#прямые-оппозиты) | все три | — | нет · кризисная фракция + нет · дикое сознание | I · начало |
| Фермер-поселенец II<br>`leader_trait_homesteader_2` | все три | — | — | II ← `leader_trait_homesteader` |
| Идеолог авторитаризма<br>`leader_trait_ideologue_authoritarian` | чиновник | Авторитаризм | — | — |
| Идеолог эгалитаризма<br>`leader_trait_ideologue_egalitarian` | чиновник | Эгалитаризм | — | — |
| Идеолог материализма<br>`leader_trait_ideologue_materialist` | чиновник | Материализм | — | — |
| Идеолог милитаризма<br>`leader_trait_ideologue_militarist` | чиновник | Милитаризм | — | — |
| Идеолог пацифизма<br>`leader_trait_ideologue_pacifist` | чиновник | Пацифизм | — | — |
| Идеолог спиритуализма<br>`leader_trait_ideologue_spiritualist` | чиновник | Спиритуализм | — | — |
| Идеолог ксенофилии<br>`leader_trait_ideologue_xenophile` | чиновник | Ксенофилия | — | — |
| Идеолог ксенофобии<br>`leader_trait_ideologue_xenophobe` | чиновник | Ксенофобия | — | — |
| Ежовые рукавицы<br>`leader_trait_iron_fist` | командир | — | нет · кризисная фракция + нет · гештальт | I · начало |
| Ежовые рукавицы II<br>`leader_trait_iron_fist_2` | командир | — | — | II ← `leader_trait_iron_fist` |
| Педантичность<br>`leader_trait_meticulous` [↔](#прямые-оппозиты) | учёный | — | — | I · начало |
| Педантичность II<br>`leader_trait_meticulous_2` [↔](#прямые-оппозиты) | учёный | — | — | II ← `leader_trait_meticulous` |
| Теоретик измерений<br>`leader_trait_planar_theorist` | учёный | — | — | I · начало |
| Теоретик измерений II<br>`leader_trait_planar_theorist_2` | учёный | — | — | II ← `leader_trait_planar_theorist` |
| Политик<br>`leader_trait_politician` | все три | вне гештальта или член совета | — | — |
| Принципиальность<br>`leader_trait_principled` | чиновник | — | — | I · начало |
| Принципиальность II<br>`leader_trait_principled_2` | чиновник | — | — | II ← `leader_trait_principled` |
| Частные шахты<br>`leader_trait_private_mines` [↔](#прямые-оппозиты) | все три | — | нет · кризисная фракция + нет · дикое сознание + нет · кочевая держава | I · начало |
| Частные шахты II<br>`leader_trait_private_mines_2` | все три | — | — | II ← `leader_trait_private_mines` |
| Выносливость<br>`leader_trait_resilient` | все три | — | нет · кризисная фракция | — |
| Заботливость<br>`leader_trait_restrained` [↔](#прямые-оппозиты) | командир | — | нет · кризисная фракция | — |
| Добродетельность<br>`leader_trait_righteous` [↔](#прямые-оппозиты) | командир, чиновник | — | нет · кризисная фракция | I · начало |
| Добродетельность II<br>`leader_trait_righteous_2` [↔](#прямые-оппозиты) | командир, чиновник | — | — | II ← `leader_trait_righteous` |
| Тяга к скитаниям<br>`leader_trait_roamer` [↔](#прямые-оппозиты) | командир, учёный | — | — | I · начало |
| Тяга к скитаниям II<br>`leader_trait_roamer_2` [↔](#прямые-оппозиты) | командир, учёный | — | — | II ← `leader_trait_roamer` |
| Разумный ИИ-помощник<br>`leader_trait_sapient_AI_assistant` [↔](#прямые-оппозиты) | учёный | — | — | — |
| Утилизатор<br>`leader_trait_scrapper` [↔](#прямые-оппозиты) | все три | — | нет · кризисная фракция + нет · дикое сознание | I · начало |
| Утилизатор II<br>`leader_trait_scrapper_2` | все три | — | — | II ← `leader_trait_scrapper` |
| Судостроитель<br>`leader_trait_shipwright` [↔](#прямые-оппозиты) | чиновник | — | — | — |
| Застрельщик<br>`leader_trait_skirmisher` | командир | — | — | — |
| Гениальность<br>`leader_trait_spark_of_genius` [↔](#прямые-оппозиты) | учёный | — | — | I · начало |
| Гениальность II<br>`leader_trait_spark_of_genius_2` [↔](#прямые-оппозиты) | учёный | — | — | II ← `leader_trait_spark_of_genius` |
| Шпионаж<br>`leader_trait_spycraft` | чиновник | — | — | I · начало |
| Шпионаж II<br>`leader_trait_spycraft_2` | чиновник | — | — | II ← `leader_trait_spycraft` |
| Специализация на торговле<br>`leader_trait_trade_focus` [↔](#прямые-оппозиты) | чиновник | — | нет · кризисная фракция + нет · гештальт | I · начало |
| Специализация на торговле II<br>`leader_trait_trade_focus_2` [↔](#прямые-оппозиты) | чиновник | — | — | II ← `leader_trait_trade_focus` |
| Хитрость<br>`leader_trait_trickster` [↔](#прямые-оппозиты) | командир | — | — | — |
| Несгибаемость<br>`leader_trait_unyielding` [↔](#прямые-оппозиты) | командир | — | — | — |
| Знаменитость<br>`leader_trait_venerated` [↔](#прямые-оппозиты) | все три | — | нет · кризисная фракция | I · начало |
| Знаменитость II<br>`leader_trait_venerated_2` | все три | — | — | II ← `leader_trait_venerated` |
| Охотник пустоты<br>`leader_trait_void_hunter` | командир | — | — | I · начало |
| Охотник пустоты II<br>`leader_trait_void_hunter_2` | командир | — | — | II ← `leader_trait_void_hunter` |
| Следопыт пустоты<br>`leader_trait_void_tracker` | учёный | — | — | I · начало |
| Следопыт пустоты II<br>`leader_trait_void_tracker_2` | учёный | — | — | II ← `leader_trait_void_tracker` |
| Голоса в голове<br>`leader_trait_whispering_mind` | все три | — | — | I · начало |
| Голоса в голове II<br>`leader_trait_whispering_mind_2` | все три | — | — | II ← `leader_trait_whispering_mind` |
| Голоса в голове III<br>`leader_trait_whispering_mind_3` | все три | — | — | III ← `leader_trait_whispering_mind_2` |
| Упор на производство линкоров<br>`trait_ruler_battleship_focus` [↔](#прямые-оппозиты) | командир | — | — | — |
| Народный избранник<br>`trait_ruler_champion_of_the_people` [↔](#прямые-оппозиты) | все три | любая личная этика, кроме гештальта | — | I · начало |
| Народный избранник II<br>`trait_ruler_champion_of_the_people_2` [↔](#прямые-оппозиты) | все три | — | — | II ← `trait_ruler_champion_of_the_people` |
| Обаятельность<br>`trait_ruler_charismatic` | все три | — | — | I · начало |
| Обаятельность II<br>`trait_ruler_charismatic_2` | все три | — | — | II ← `trait_ruler_charismatic` |
| Упор на производство корветов<br>`trait_ruler_corvette_focus` [↔](#прямые-оппозиты) | командир | — | — | — |
| Упор на производство крейсеров<br>`trait_ruler_cruiser_focus` [↔](#прямые-оппозиты) | командир | — | — | — |
| Упор на производство эсминцев<br>`trait_ruler_destroyer_focus` [↔](#прямые-оппозиты) | командир | — | — | — |
| Поиск талантов<br>`trait_ruler_eye_for_talent` | все три | — | — | I · начало |
| Поиск талантов II<br>`trait_ruler_eye_for_talent_2` | все три | — | — | II ← `trait_ruler_eye_for_talent` |
| Цепь обратной связи<br>`trait_ruler_feedback_loop` [↔](#прямые-оппозиты) | все три | личная этика гештальта | — | I · начало |
| Цепь обратной связи II<br>`trait_ruler_feedback_loop_2` [↔](#прямые-оппозиты) | все три | — | — | II ← `trait_ruler_feedback_loop` |
| Сторонник рождаемости<br>`trait_ruler_fertility_preacher` | чиновник | — | нет · кризисная фракция + нет · дикое сознание | — |
| Первопроходец<br>`trait_ruler_frontier_spirit` | чиновник | — | нет · дикое сознание | — |
| Родина в небе<br>`trait_ruler_home_in_the_sky` | учёный | — | — | — |
| Минеральная лихорадка<br>`trait_ruler_industrialist` | чиновник, учёный | — | — | I · начало |
| Минеральная лихорадка II<br>`trait_ruler_industrialist_2` | чиновник, учёный | — | — | II ← `trait_ruler_industrialist` |
| Понимание логистики<br>`trait_ruler_logistic_understanding` | все три | — | — | I · начало |
| Понимание логистики II<br>`trait_ruler_logistic_understanding_2` | все три | — | — | II ← `trait_ruler_logistic_understanding` |
| Космический шахтёр<br>`trait_ruler_space_miner` | учёный | — | — | — |
| Воинственность<br>`trait_ruler_warlike` | командир | — | — | I · начало |
| Воинственность II<br>`trait_ruler_warlike_2` | командир | — | — | II ← `trait_ruler_warlike` |

## Черты резерва лидеров

7 ID.

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Фермерское происхождение<br>`leader_trait_agrarian_upbringing` | все три | — | нет · кризисная фракция + нет · дикое сознание | — |
| Ветеран армии<br>`leader_trait_army_veteran` [↔](#прямые-оппозиты) | чиновник, учёный | — | — | — |
| Усердность<br>`leader_trait_eager` | все три | — | нет · кризисная фракция | — |
| Питомец для эмоциональной поддержки<br>`leader_trait_emotional_support_pet` | все три | — | нет · машинный разум | — |
| Обычная держава — Одарённый / Улей — Одарённый / Машинный разум — Улучшенный<br>`leader_trait_gifted` | все три | — | нет · кризисная фракция | I · начало |
| Обычная держава — Одарённый II / Улей — Одарённый II / Машинный разум — Улучшенный II<br>`leader_trait_gifted_2` | все три | — | — | II ← `leader_trait_gifted` |
| Отставной офицер флота<br>`leader_trait_retired_fleet_officer` [↔](#прямые-оппозиты) | чиновник, учёный | — | — | — |

## Только для стартового правителя

9 ID.

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Буканьер<br>`leader_trait_buccaneer` | все три | — | — | I · начало |
| Буканьер II<br>`leader_trait_buccaneer_2` | все три | — | — | II ← `leader_trait_buccaneer` |
| Буканьер III<br>`leader_trait_buccaneer_3` | все три | — | — | III ← `leader_trait_buccaneer_2` |
| Первопроходец<br>`leader_trait_trailblazer` | все три | — | — | I · начало |
| Первопроходец II<br>`leader_trait_trailblazer_2` | все три | — | — | II ← `leader_trait_trailblazer` |
| Первопроходец III<br>`leader_trait_trailblazer_3` | все три | — | — | III ← `leader_trait_trailblazer_2` |
| Собиратель сокровищ<br>`leader_trait_treasure_hoarder` | все три | — | — | I · начало |
| Собиратель сокровищ II<br>`leader_trait_treasure_hoarder_2` | все три | — | — | II ← `leader_trait_treasure_hoarder` |
| Собиратель сокровищ III<br>`leader_trait_treasure_hoarder_3` | все три | — | — | III ← `leader_trait_treasure_hoarder_2` |

## Черты вида и возвышения

10 ID.

### Генетика и клонирование

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Эрудит<br>`leader_trait_erudite` [↔](#прямые-оппозиты) | все три | — | нет · дикое сознание | — |
| Запасной клон<br>`leader_trait_has_backup_clone` | все три | нероботический вид | — | — |
| Приверженец генетической чистоты<br>`trait_leader_genetic_purist` | все три | нероботический вид | улей исключён | — |
| Второй шанс<br>`trait_leader_second_chanced` | все три | нероботический вид | — | — |

### Кибернетика

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Киборг<br>`leader_trait_cyborg` [↔](#прямые-оппозиты) | все три | — | — | — |
| Нейрологический брандмауэр<br>`leader_trait_firewalled` | все три | кибернетический вид или черта «Киборг» | — | — |
| Минимальная киборгизация<br>`leader_trait_limited_cyborg` [↔](#прямые-оппозиты) | все три | личная этика — спиритуализм | — | — |

### Синтетика и виртуальность

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Синтетик<br>`leader_trait_synthetic` [↔](#прямые-оппозиты) | все три | — | — | — |
| Виртуальный лидер<br>`leader_trait_virtual` | все три | роботический вид | — | — |

### Псионика

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Экстрасенс<br>`leader_trait_psionic` [↔](#прямые-оппозиты) | все три | — | — | — |

## Черты происхождений

42 ID.

### Под единой властью

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Заносчивость<br>`leader_trait_legendary_bad_meritocracy` [↔](#прямые-оппозиты) | все три | правитель | — | — |
| Тиран-параноик<br>`leader_trait_legendary_delusional` | все три | правитель | — | — |
| Рассеянность<br>`leader_trait_legendary_dreamlike` [↔](#прямые-оппозиты) | все три | правитель | — | — |
| Безжалостность<br>`leader_trait_legendary_harsh_ruler` [↔](#прямые-оппозиты) | все три | правитель | — | — |
| Трусость<br>`leader_trait_legendary_hoplofobia` [↔](#прямые-оппозиты) | все три | правитель | — | — |
| Светило<br>`leader_trait_legendary_leader` | все три | правитель | — | — |
| Потомок Светила<br>`leader_trait_legendary_offspring` | все три | наследник | — | — |
| Наивность<br>`leader_trait_legendary_too_open` [↔](#прямые-оппозиты) | все три | правитель | — | — |
| Прямолинейность<br>`leader_trait_legendary_unfriendly` [↔](#прямые-оппозиты) | все три | правитель | — | — |
| Милитарист<br>`leader_trait_legendary_warmonger` [↔](#прямые-оппозиты) | все три | правитель | — | — |
| Раб аппарата<br>`leader_trait_the_apparatus_luminary` | все три | правитель | — | — |
| Бесконечные улучшения<br>`leader_trait_the_cybernetic_luminary` | все три | правитель | — | — |
| Генетическое совершенство<br>`leader_trait_the_genetic_luminary` | все три | правитель | — | — |
| Пассажир<br>`leader_trait_the_psionic_luminary` | все три | правитель | — | — |
| Синтетическое сознание<br>`leader_trait_the_synth_luminary` | все три | правитель | — | — |

### Страх темноты

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Изворотливость<br>`leader_trait_fotd_commander` | командир | — | — | — |
| Изворотливость<br>`leader_trait_fotd_scientist` | учёный | — | — | — |

### Золотое поколение

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Инженер обороны<br>`leader_trait_defence_engineer_scientist` | учёный | — | нет · кочевая держава | — |
| Элитный выпускник<br>`leader_trait_elite_alumnus` | все три | — | — | — |
| Организатор флота<br>`leader_trait_fleet_organizer_official` [↔](#прямые-оппозиты) | чиновник | — | — | — |
| Золотой соратник<br>`leader_trait_golden_cooperator` | все три | — | — | — |
| Золотой одиночка<br>`leader_trait_golden_exclusivist` | все три | — | — | — |
| Золотое поколение<br>`leader_trait_golden_generation` | все три | — | — | — |
| Трансплантация органа<br>`leader_trait_organ_transplant` | все три | — | — | — |
| Судостроитель<br>`leader_trait_shipwright_scientist` [↔](#прямые-оппозиты) | учёный | — | — | — |
| Гениальность<br>`leader_trait_spark_of_genius_other_classes` [↔](#прямые-оппозиты) | командир, чиновник | — | — | — |
| Шпионаж<br>`leader_trait_spycraft_commander` | командир | — | — | — |
| Воинственность<br>`trait_ruler_warlike_all_classes` | все три | — | — | — |

### Армия клонов

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Командир армии клонов<br>`leader_trait_clone_army_commander` | командир | нероботический вид | — | — |
| Потомственный командир армии клонов<br>`leader_trait_clone_army_fertile_commander` | командир | нероботический вид | — | — |
| Улучшенный командир армии клонов<br>`leader_trait_clone_army_full_commander` | командир | нероботический вид | — | — |

### Охотники за бурями

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Оседлавший бурю<br>`leader_trait_storm_rider_commander` | командир | — | — | — |
| Оседлавший бурю<br>`leader_trait_storm_rider_official` | чиновник | — | — | — |
| Оседлавший бурю<br>`leader_trait_storm_rider_scientist` | учёный | — | — | — |

### Отпрыски

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Древнее знание<br>`leader_trait_ancient_knowledge` | все три | — | — | — |

### Полный сброс

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Солдат-киборг<br>`leader_trait_unplugged_cybernetic_positives_1` | командир | — | — | сюжетное состояние |
| Киберштурмовик<br>`leader_trait_unplugged_cybernetic_positives_2` | командир | — | — | сюжетное состояние |
| Киберкоммандо<br>`leader_trait_unplugged_cybernetic_positives_3` | командир | — | — | сюжетное состояние |

### Кибернетический культ

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Ритуальные импланты<br>`leader_trait_ritualistic_implants_cyborg` [↔](#прямые-оппозиты) | все три | нероботический вид | — | — |

### Синтетическая репродуктивность

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Робот-суррогат<br>`leader_trait_robotic_surrogate` | все три | роботический вид | — | — |

### Покроворождённые

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Ведомый<br>`leader_trait_guided` | учёный | — | — | — |
| Пророк Покрова<br>`leader_trait_shroud_prophet` | чиновник | роботический вид | — | — |

## Черты державы и должности

24 ID.

### Правители и наследники

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| ⟨Титул правителя державы⟩<br>`leader_trait_ruler_hive_mind` | все три | правитель | коллективный разум (улей) | — |
| Машинный разум<br>`leader_trait_ruler_machine_intelligence` | все три | правитель | машинный разум | — |
| Правитель — Правитель империи / Наследник — Имперский наследник / Другой член династии — Имперская родословная<br>`trait_imperial_heir` | все три | — | — | — |

### Специализированные вассалы

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Мститель бастиона<br>`leader_trait_bulwark_retaliator` | командир | — | — | — |
| Страж бастиона<br>`leader_trait_bulwark_sentinel` | командир | — | — | — |
| Наблюдатель бастиона<br>`leader_trait_bulwark_watcher` | командир | — | — | — |
| Экстрактор проспектория<br>`leader_trait_prospectorium_extractor` | чиновник | — | — | — |
| Оптимизатор проспектория<br>`leader_trait_prospectorium_optimizer` | чиновник | — | — | — |
| Очиститель проспектория<br>`leader_trait_prospectorium_refiner` | чиновник | — | — | — |
| Исследователь схолария<br>`leader_trait_scholarium_explorer` | учёный | — | — | — |
| Учёный схолария<br>`leader_trait_scholarium_investigator` | учёный | — | — | — |
| Наблюдатель схолария<br>`leader_trait_scholarium_observer` | учёный | — | — | — |

### Культурные посланники

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Воспитатель<br>`leader_trait_cultural_envoy_indoctrinator` | чиновник | — | — | — |
| Переговорщик<br>`leader_trait_cultural_envoy_negotiator` | чиновник | — | — | — |
| Светило убедительности<br>`leader_trait_cultural_envoy_persuasive_luminary` | чиновник | — | — | — |
| Фанатик<br>`leader_trait_cultural_envoy_zealot` | чиновник | — | — | — |

### Паладины

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Паладин<br>`leader_trait_paladin` | командир | — | — | — |
| Пилот-ас<br>`leader_trait_paladin_ace` | командир | — | — | — |
| Рейнджер<br>`leader_trait_paladin_ambusher` | командир | — | — | — |
| Защитник<br>`leader_trait_paladin_defender` | командир | — | — | — |
| Рыцарь<br>`leader_trait_paladin_knight` | командир | — | — | — |
| Гений логистики<br>`leader_trait_paladin_logistician` | командир | — | — | — |
| Остриё копья<br>`leader_trait_paladin_spearhead` | командир | — | — | — |
| Хитроумный стратег<br>`leader_trait_paladin_strategist` | командир | — | — | — |

## Событийные черты

43 ID.

### Покров

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Озарённый Покровом дрон-командир<br>`gestalt_trait_commander_mind_wipe_01` | командир | — | гештальт | — |
| Озарённый Покровом дрон-командир<br>`gestalt_trait_commander_mind_wipe_02` | командир | — | гештальт | — |
| Озарённый Покровом дрон-штурмовик<br>`gestalt_trait_general_mind_wipe_01` | командир | — | гештальт | — |
| Озарённый Покровом дрон-штурмовик<br>`gestalt_trait_general_mind_wipe_02` | командир | — | гештальт | — |
| Озарённый Покровом командующий дрон<br>`gestalt_trait_ruler_mind_wipe_01` | все три | выдача не подтверждена¹ | гештальт | — |
| Озарённый Покровом командующий дрон<br>`gestalt_trait_ruler_mind_wipe_02` | все три | выдача не подтверждена¹ | гештальт | — |
| Озарённый Покровом дрон-исследователь<br>`gestalt_trait_scientist_mind_wipe_02` | учёный | — | гештальт | — |
| Озарённый Покровом командир<br>`leader_trait_admiral_mind_wipe_01` | командир | — | вне гештальта | — |
| Озарённый Покровом командир<br>`leader_trait_admiral_mind_wipe_02` | командир | — | вне гештальта | — |
| Обычная держава — Избранный / Гештальт — Избранный сосуд<br>`leader_trait_chosen` [↔](#прямые-оппозиты) | все три | — | — | — |
| Избранный<br>`leader_trait_composer_chosen` [↔](#прямые-оппозиты) | все три | — | — | — |
| Избранный Колыбелью<br>`leader_trait_cradle_chosen` [↔](#прямые-оппозиты) | все три | — | — | — |
| Избранный<br>`leader_trait_eater_chosen` [↔](#прямые-оппозиты) | все три | — | — | — |
| Озарённый Покровом командир<br>`leader_trait_general_mind_wipe_01` | командир | — | вне гештальта | — |
| Озарённый Покровом командир<br>`leader_trait_general_mind_wipe_02` | командир | — | вне гештальта | — |
| Избранный<br>`leader_trait_instrument_chosen` [↔](#прямые-оппозиты) | все три | — | — | — |
| Озарённый Покровом архитектор<br>`leader_trait_ruler_mind_wipe_01` | командир, учёный | — | вне гештальта | — |
| Озарённый Покровом логист<br>`leader_trait_ruler_mind_wipe_02` | командир, учёный | — | вне гештальта | — |
| Озарённый Покровом учёный<br>`leader_trait_scientist_mind_wipe_01` | учёный | — | вне гештальта | — |
| Озарённый Покровом учёный<br>`leader_trait_scientist_mind_wipe_02` | учёный | — | вне гештальта | — |
| Увеличенная продолжительность жизни<br>`leader_trait_shroud_age` | все три | — | — | — |
| Искажённый Покровом<br>`leader_trait_shroud_warped` | все три | — | — | — |
| Ваятель Покрова<br>`leader_trait_shroudshaper` | все три | — | — | — |
| Избранный Шепчущих<br>`leader_trait_whisperers_chosen` [↔](#прямые-оппозиты) | все три | — | — | — |

### Аномалии и исследования

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Изменённый метаболизм<br>`leader_trait_altered_metabolism` | учёный | — | — | — |
| Носитель мозгового слизня<br>`leader_trait_brainslug` | все три | — | — | — |
| Вдохновлённый археолог<br>`leader_trait_inspired_archaeologist` | учёный | выдача не подтверждена¹ | — | — |
| Вдохновлённый исследователь<br>`leader_trait_inspired_researcher` | учёный | выдача не подтверждена¹ | — | — |
| Вдохновлённый топограф<br>`leader_trait_inspired_surveyor` | учёный | выдача не подтверждена¹ | — | — |
| Вне времени<br>`leader_trait_intemporal` | все три | — | — | — |
| Силовой ремонт<br>`leader_trait_percussive_maintainer` | учёный | — | — | — |
| Хранитель полотенца<br>`leader_trait_towel` | учёный | — | — | — |

### Астральные разломы

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Искажённость разломом<br>`leader_trait_rift_warped` | все три | — | — | — |
| Санитарная единица-помощник<br>`leader_trait_sanitary_drone` | учёный | — | — | — |

### Левиафаны

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Убийца дракона<br>`leader_trait_dragonslayer` | командир | — | — | — |

### Приключения ковчегов

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Чемпион кольцевой гонки<br>`leader_trait_circuit_champion` | все три | — | — | — |
| Пилот «Соболь»<br>`leader_trait_sable_pilot` | командир | — | — | — |

### Прочие сюжетные цепочки

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Противовес караванов<br>`leader_trait_caravan_counter` | командир | — | — | — |
| Предрешённая судьбой встреча<br>`leader_trait_foredoomed_to_a_rendezvous` | командир | — | — | — |
| Интеллектуальность<br>`leader_trait_intellectual` | чиновник | — | — | — |
| Закалка чумой<br>`leader_trait_plague_hardened` | командир | — | — | — |
| Деловая смекалка<br>`leader_trait_preftl_haggler` | чиновник | — | — | — |
| Непоколебимая вера<br>`leader_trait_zealot` | чиновник | — | — | — |

## Черты особых лидеров

26 ID.

### Уникальные персонажи

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| ИИ-помощник Горький<br>`leader_trait_gorky` | учёный | — | — | — |
| Нанитовое существо<br>`leader_trait_governor_gray` | чиновник | — | — | — |
| Оракул<br>`leader_trait_governor_oracle` | чиновник | — | — | — |
| Псионическое единение<br>`leader_trait_governor_psionic_communion` [↔](#прямые-оппозиты) | чиновник | — | — | — |
| Наследие предков<br>`leader_trait_legendary_ancestors_knowledge` | все три | — | — | — |
| Туманное прошлое<br>`leader_trait_legendary_far_from_home` | учёный | — | — | — |
| Терраформирующее ядро<br>`leader_trait_legendary_terraformation_nucleus_1_bud` | учёный | — | — | сюжетное состояние |
| Терраформирующие ядра<br>`leader_trait_legendary_terraformation_nucleus_2_buds` | учёный | — | — | сюжетное состояние |
| Терраформирующие ядра<br>`leader_trait_legendary_terraformation_nucleus_3_buds` | учёный | — | — | сюжетное состояние |

### Анклавы и караванщики

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Куратор<br>`leader_trait_curator` | учёный | — | — | — |
| Торговец анклава<br>`leader_trait_enclave_trader` | чиновник | выдача не подтверждена¹ | — | — |
| Мастер-утилизатор<br>`leader_trait_master_salvager` | учёный | — | — | — |
| Воин-наёмник<br>`leader_trait_mercenary_warrior` | командир | — | — | — |
| Муутаганский посредник<br>`leader_trait_muutagan_liaison` | чиновник | — | — | — |
| Торговец Нумы<br>`leader_trait_nuumismatic_priest` | чиновник | — | — | — |
| Ригганский посредник<br>`leader_trait_riggan_liaison` | чиновник | — | — | — |
| Наставник Идущих-сквозь-Покров<br>`leader_trait_shroudwalker` | чиновник | — | — | — |
| Специалист по утилизации отходов<br>`leader_trait_waste_management_specialist` | чиновник | — | — | — |
| Посредник корпорации «Ксура»<br>`leader_trait_xuracorp_liaison` | чиновник | — | — | — |

### Кризисы и особые фракции

| Черта и ID | Класс | Лидер | Держава | Ранг |
|---|---|---|---|---|
| Базы данных Сайбрекса<br>`leader_trait_cybrex` | командир | роботический вид | гештальт | — |
| Межпространственные рывки<br>`leader_trait_dimensional_stutter` | командир | — | кризисная фракция | — |
| Бесплотность<br>`leader_trait_ethereal` | командир | — | кризисная фракция | — |
| Взаимосвязь улья<br>`leader_trait_hive_affinity` | командир | — | кризисная фракция | — |
| Великий хан<br>`leader_trait_ruler_great_khan` | все три | правитель | — | — |
| Выучка Стражей<br>`leader_trait_sentinel` | командир | — | — | — |
| Охотник пустоты<br>`leader_trait_void_swimmer` | командир | — | кризисная фракция | — |

## Прямые оппозиты

Кнопка скрыта, если у лидера есть хотя бы один из перечисленных в её строке ID. Проверяется прямой список `opposites` именно выдаваемого ранга. У 64 кнопок он заполнен. В основных таблицах они отмечены знаком ↔.

| Выдаваемый ID | Прямые оппозиты этого ID |
|---|---|
| `leader_trait_adaptable` | `leader_trait_stubborn`, `leader_trait_stubborn_2` |
| `leader_trait_aggressive` | `leader_trait_cautious` |
| `leader_trait_architectural_interest` | `leader_trait_procrastinator`, `leader_trait_procrastinator_2` |
| `leader_trait_army_veteran` | `leader_trait_retired_fleet_officer` |
| `leader_trait_butcher` | `leader_trait_armchair_commander`, `leader_trait_armchair_commander_2`, `leader_trait_restrained` |
| `leader_trait_capitalist` | `leader_trait_private_mines`, `leader_trait_private_mines_2`, `leader_trait_homesteader`, `leader_trait_homesteader_2`, `leader_trait_scrapper`, `leader_trait_scrapper_2`, `leader_trait_entrepreneur`, `leader_trait_entrepreneur_2`, `leader_trait_venerated`, `leader_trait_venerated_2` |
| `leader_trait_carefree` | `leader_trait_meticulous`, `leader_trait_meticulous_2`, `leader_trait_neurotic`, `leader_trait_neurotic_2` |
| `leader_trait_carefree_2` | `leader_trait_meticulous`, `leader_trait_meticulous_2`, `leader_trait_neurotic`, `leader_trait_neurotic_2` |
| `leader_trait_cautious` | `leader_trait_aggressive` |
| `leader_trait_chosen` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `leader_trait_composer_chosen` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `leader_trait_cradle_chosen` | `leader_trait_cyborg`, `leader_trait_synthetic` |
| `leader_trait_custom_AI_assistant` | `leader_trait_sapient_AI_assistant` |
| `leader_trait_cyborg` | `leader_trait_erudite`, `leader_trait_chosen`, `leader_trait_limited_cyborg`, `leader_trait_psionic`, `leader_trait_synthetic` |
| `leader_trait_eater_chosen` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `leader_trait_entrepreneur` | `leader_trait_capitalist`, `leader_trait_capitalist_2`, `leader_trait_private_mines`, `leader_trait_private_mines_2`, `leader_trait_homesteader`, `leader_trait_homesteader_2`, `leader_trait_scrapper`, `leader_trait_scrapper_2`, `leader_trait_venerated`, `leader_trait_venerated_2` |
| `leader_trait_erudite` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `leader_trait_fleet_organizer` | `leader_trait_nervous`, `leader_trait_nervous_2` |
| `leader_trait_fleet_organizer_2` | `leader_trait_nervous`, `leader_trait_nervous_2` |
| `leader_trait_fleet_organizer_official` | `leader_trait_nervous`, `leader_trait_nervous_2` |
| `leader_trait_governor_psionic_communion` | `leader_trait_cyborg`, `leader_trait_synthetic` |
| `leader_trait_homesteader` | `leader_trait_capitalist`, `leader_trait_capitalist_2`, `leader_trait_private_mines`, `leader_trait_private_mines_2`, `leader_trait_scrapper`, `leader_trait_scrapper_2`, `leader_trait_entrepreneur`, `leader_trait_entrepreneur_2`, `leader_trait_venerated`, `leader_trait_venerated_2` |
| `leader_trait_instrument_chosen` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `leader_trait_legendary_bad_meritocracy` | `leader_trait_legendary_unfriendly`, `leader_trait_legendary_warmonger`, `leader_trait_legendary_dreamlike`, `leader_trait_legendary_harsh_ruler`, `leader_trait_legendary_too_open`, `leader_trait_legendary_hoplofobia` |
| `leader_trait_legendary_dreamlike` | `leader_trait_legendary_unfriendly`, `leader_trait_legendary_warmonger`, `leader_trait_legendary_harsh_ruler`, `leader_trait_legendary_too_open`, `leader_trait_legendary_hoplofobia`, `leader_trait_legendary_bad_meritocracy` |
| `leader_trait_legendary_harsh_ruler` | `leader_trait_legendary_unfriendly`, `leader_trait_legendary_warmonger`, `leader_trait_legendary_dreamlike`, `leader_trait_legendary_too_open`, `leader_trait_legendary_hoplofobia`, `leader_trait_legendary_bad_meritocracy` |
| `leader_trait_legendary_hoplofobia` | `leader_trait_legendary_unfriendly`, `leader_trait_legendary_warmonger`, `leader_trait_legendary_dreamlike`, `leader_trait_legendary_harsh_ruler`, `leader_trait_legendary_too_open`, `leader_trait_legendary_bad_meritocracy` |
| `leader_trait_legendary_too_open` | `leader_trait_legendary_unfriendly`, `leader_trait_legendary_warmonger`, `leader_trait_legendary_dreamlike`, `leader_trait_legendary_harsh_ruler`, `leader_trait_legendary_hoplofobia`, `leader_trait_legendary_bad_meritocracy` |
| `leader_trait_legendary_unfriendly` | `leader_trait_legendary_warmonger`, `leader_trait_legendary_dreamlike`, `leader_trait_legendary_harsh_ruler`, `leader_trait_legendary_too_open`, `leader_trait_legendary_hoplofobia`, `leader_trait_legendary_bad_meritocracy` |
| `leader_trait_legendary_warmonger` | `leader_trait_legendary_unfriendly`, `leader_trait_legendary_dreamlike`, `leader_trait_legendary_harsh_ruler`, `leader_trait_legendary_too_open`, `leader_trait_legendary_hoplofobia`, `leader_trait_legendary_bad_meritocracy` |
| `leader_trait_limited_cyborg` | `leader_trait_psionic`, `leader_trait_chosen` |
| `leader_trait_meticulous` | `leader_trait_carefree`, `leader_trait_carefree_2` |
| `leader_trait_meticulous_2` | `leader_trait_carefree`, `leader_trait_carefree_2` |
| `leader_trait_private_mines` | `leader_trait_capitalist`, `leader_trait_capitalist_2`, `leader_trait_homesteader`, `leader_trait_homesteader_2`, `leader_trait_scrapper`, `leader_trait_scrapper_2`, `leader_trait_entrepreneur`, `leader_trait_entrepreneur_2`, `leader_trait_venerated`, `leader_trait_venerated_2` |
| `leader_trait_psionic` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `leader_trait_restrained` | `leader_trait_victory_or_death`, `leader_trait_victory_or_death_2`, `leader_trait_butcher` |
| `leader_trait_retired_fleet_officer` | `leader_trait_army_veteran` |
| `leader_trait_righteous` | `leader_trait_corrupt`, `leader_trait_corrupt_2` |
| `leader_trait_righteous_2` | `leader_trait_corrupt`, `leader_trait_corrupt_2` |
| `leader_trait_ritualistic_implants_cyborg` | `leader_trait_psionic`, `leader_trait_chosen` |
| `leader_trait_roamer` | `leader_trait_neurotic`, `leader_trait_neurotic_2` |
| `leader_trait_roamer_2` | `leader_trait_neurotic`, `leader_trait_neurotic_2` |
| `leader_trait_sapient_AI_assistant` | `leader_trait_custom_AI_assistant` |
| `leader_trait_scrapper` | `leader_trait_capitalist`, `leader_trait_capitalist_2`, `leader_trait_private_mines`, `leader_trait_private_mines_2`, `leader_trait_homesteader`, `leader_trait_homesteader_2`, `leader_trait_entrepreneur`, `leader_trait_entrepreneur_2`, `leader_trait_venerated`, `leader_trait_venerated_2` |
| `leader_trait_shipwright` | `leader_trait_irenic`, `leader_trait_irenic_2` |
| `leader_trait_shipwright_scientist` | `leader_trait_irenic`, `leader_trait_irenic_2` |
| `leader_trait_spark_of_genius` | `leader_trait_paranoid`, `leader_trait_paranoid_2` |
| `leader_trait_spark_of_genius_2` | `leader_trait_paranoid`, `leader_trait_paranoid_2` |
| `leader_trait_spark_of_genius_other_classes` | `leader_trait_paranoid`, `leader_trait_paranoid_2` |
| `leader_trait_synthetic` | `leader_trait_erudite`, `leader_trait_chosen`, `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_psionic` |
| `leader_trait_trade_focus` | `leader_trait_insider_trading`, `leader_trait_insider_trading_2` |
| `leader_trait_trade_focus_2` | `leader_trait_insider_trading`, `leader_trait_insider_trading_2` |
| `leader_trait_trickster` | `leader_trait_unyielding`, `leader_trait_reckless`, `leader_trait_reckless_2` |
| `leader_trait_unyielding` | `leader_trait_nervous`, `leader_trait_nervous_2`, `leader_trait_slipshod`, `leader_trait_slipshod_2`, `leader_trait_trickster` |
| `leader_trait_venerated` | `leader_trait_capitalist`, `leader_trait_capitalist_2`, `leader_trait_private_mines`, `leader_trait_private_mines_2`, `leader_trait_homesteader`, `leader_trait_homesteader_2`, `leader_trait_scrapper`, `leader_trait_scrapper_2`, `leader_trait_entrepreneur`, `leader_trait_entrepreneur_2` |
| `leader_trait_whisperers_chosen` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `trait_ruler_battleship_focus` | `trait_ruler_corvette_focus`, `trait_ruler_destroyer_focus`, `trait_ruler_cruiser_focus` |
| `trait_ruler_champion_of_the_people` | `leader_trait_tyrannical`, `leader_trait_tyrannical_2` |
| `trait_ruler_champion_of_the_people_2` | `leader_trait_tyrannical`, `leader_trait_tyrannical_2` |
| `trait_ruler_corvette_focus` | `trait_ruler_destroyer_focus`, `trait_ruler_cruiser_focus`, `trait_ruler_battleship_focus` |
| `trait_ruler_cruiser_focus` | `trait_ruler_corvette_focus`, `trait_ruler_destroyer_focus`, `trait_ruler_battleship_focus` |
| `trait_ruler_destroyer_focus` | `trait_ruler_corvette_focus`, `trait_ruler_cruiser_focus`, `trait_ruler_battleship_focus` |
| `trait_ruler_feedback_loop` | `leader_trait_tyrannical`, `leader_trait_tyrannical_2` |
| `trait_ruler_feedback_loop_2` | `leader_trait_tyrannical`, `leader_trait_tyrannical_2` |

## Особые случаи и источники

- «Политик» проверяет личную этику. Если у лидера гештальт-сознание, достаточно места в совете. Машинный разум владельца сам по себе ответ на эту проверку не даёт.
- В `enclave.6010` игра выбирает вариант озарения по типу державы и классу. Два обычных варианта с `ruler` в ID могут получить как командиры, так и учёные. Чиновники в этом розыгрыше отсутствуют. ¹ Два дронских варианта правителя встречаются только в проверке наличия у гештальта. Для меню сохраняется этот фильтр державы и все три класса из определения. У трёх черт вдохновения и у торговца анклава также не установлена прямая ванильная выдача. У всех шести черт сохранены классы из определений.
- «Эрудита» выдаёт в том числе контракт «Вечный хор» (`arkship.145`). Поэтому редактор не требует генетической черты вида. Псионику могут иметь и роботы, что прямо учитывает `update_leader_after_modification`. У «Ограниченной киборгизации» проверяется личный спиритуализм. Для выдачи «Второго шанса» `bio.765` проверяет вид с запасными органами, а у этого признака разрешены биологический и литоидный архетипы.
- Для «Носителя мозгового слизня» отбор новых лидеров в `distar.173` ограничивает вид. `distar.172` также выдаёт черту руководителю экспедиции напрямую. Ограничение из позднего розыгрыша нельзя распространить на каждый способ выдачи. «Санитарный дрон» (`astral_rift.2675`) выдаётся учёному экспедиции без проверки гештальта.
- Ветвь кризисов включает разные фракции. Межпространственные захватчики и преторины входят в `is_crisis_faction`. Страна Сайбрекса создана как `cybrex_empire` с гештальт-этикой и роботическим видом. Отдельная кочевая выдача Великого хана использует текущего правителя.

Идентификаторы, определения, места выдачи и ванильные ограничения для каждого ранга приведены в последних колонках исходной таблицы. Ссылки на файлы и номера строк даны относительно установленной Stellaris 4.6.0. [Исходная таблица](BASIC_LEADER_TRAITS_4_6_0_RU.csv) · [Исследование лидеров](VANILLA_LEADERS_4_6_0_RU.md#видимость-меню-добавления-черт)
