# Сервер WEB_STTV. Словарь формулировок технологических тултипов

## Оглавление

- [Что входит в словарь](#что-входит-в-словарь)
- [Предметные проверки](#предметные-проверки)
- [Область действия и общие проверки](#область-действия-и-общие-проверки)
- [Логика, вес и параметры](#логика-вес-и-параметры)
- [Названия из игры](#названия-из-игры)
- [Приёмка](#приёмка)

## Что входит в словарь

**Реализован раздел предметных проверок.** Для 70 проверок опубликованы 87 пар строк RU/EN. Например, для `has_technology` используются ключ `sttv_tooltip_has_technology` и два шаблона — «Исследована технология „{technology}“» и “Has researched the technology ‘{technology}’”. Название передаёт существующая функция локализации. Это одна запись для всех технологий. [Русские строки](../../../localization/russian/sttv_tooltip_conditions_l_russian.yml) · [Английские строки](../../../localization/english/sttv_tooltip_conditions_l_english.yml)

Оба проектных каталога входят в профиль локализации. Контекст `tooltip_condition` формирует ключ по имени конструкции. Для логического значения `no` предусмотрен суффикс `_no`. Для `has_trait` подготовлены отдельные подписи `_species` и `_leader`. При сборке фразы вызывающий код выбирает подходящий вариант и подставляет значения в именованные параметры. В числовых шаблонах `{comparison}` обозначает знак сравнения, `{value}` — значение, а `{percentage}` — уже отформатированную долю с обозначением процентов. [ТЗ содержимого тултипа](../../../Docs/frontend/TZ_TECHNOLOGY_TOOLTIP_CONTENT_RU.md)

**Список ниже получен из MongoDB.** Проверены все 679 документов `wiki.technologies`. Из корня каждой базовой технологии взяты все вхождения `prerequisites` (505 технологий), `potential` (376), `allow` (0) и `weight_modifier` (555). Рекурсивный обход их раскрытых деревьев дал **121 различный ключ записи**. Имена корневых разделов, логические узлы и скалярные аргументы посчитаны отдельно. Выборка охватывает базовые технологии до фильтрации дерева по DLC.

## Предметные проверки

Для следующих **70 ключей** нужны формулировки того, что проверяет игра. Родственные проверки могут использовать общий шаблон. Например, у `has_seen_any_bypass` важно передать факт обнаружения перехода, у `owns_any_bypass` — владение им.

| Группа | Игровые ключи |
|---|---|
| Исследования и развитие | `has_technology`, `can_research_technology`, `has_tradition`, `has_ascension_perk`, `has_crisis_level`, `has_menace_perk`, `num_ascension_perk_slots` |
| Устройство империи и дополнения | `host_has_dlc`, `has_origin`, `has_authority`, `has_civic`, `has_valid_civic`, `has_ethic`, `has_ai_personality`, `is_ai`, `is_country_type`, `is_nomadic`, `uses_ship_category` |
| Виды, население и лидеры | `has_trait`, `is_archetype`, `has_dna`, `is_same_species`, `is_sapient`, `has_citizenship_type`, `has_slavery_type`, `is_pop_category`, `count_owned_pop_amount`, `is_councilor`, `is_councilor_type`, `is_ruler`, `has_base_skill` |
| Дипломатия, федерация и сообщество | `has_communications`, `num_communications`, `perc_communications_with_playable`, `has_federation`, `has_federation_law`, `has_federation_perk`, `is_galactic_community_member`, `is_active_resolution`, `is_subject`, `has_active_specialization` |
| Планеты, ресурсы и строительство | `num_owned_planets`, `is_planet_class`, `has_deposit`, `has_deposit_for`, `has_district`, `uses_district_set`, `num_districts`, `num_zones`, `num_buildings`, `has_resource`, `resource_expenses_compare`, `has_megastructure`, `has_starbase_size`, `count_starbase_sizes` |
| Время, исследование галактики и переходы | `years_passed`, `mid_game_years_passed`, `days_passed`, `num_cosmic_storms_encountered`, `is_astral_scar`, `is_inside_nebula`, `count_archaeological_site`, `is_site_completed`, `has_relic`, `has_seen_any_bypass`, `owns_any_bypass` |
| Флаги и модификаторы | `has_policy_flag`, `has_country_flag`, `has_global_flag`, `has_modifier` |

## Область действия и общие проверки

Ещё **27 ключей** определяют, у кого проверяется условие, сколько объектов должно ему удовлетворять или как трактовать результат. Например, у «Титанов» `any_neighbor_country` вместе с `has_technology` читается как «Хотя бы одна соседняя империя исследовала технологию „Титаны“». [Игровой пример](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:236)

Этот раздел реализован. Опубликованы **28 пар строк** для всех 27 ключей, включая две формы для `always = yes/no`. Перебор и переходы задают подпись группы. Подпись и дочерние проверки читаются в порядке вложенности. Так, `federation → any_member → has_technology` означает, что технологию исследовал хотя бы один член данной федерации. Ключ `sttv_tooltip_space_owner?` запрашивается напрямую, со знаком вопроса, и обозначает владельца территории системы, если он есть. [Русские строки](../../../localization/russian/sttv_tooltip_scopes_l_russian.yml) · [Английские строки](../../../localization/english/sttv_tooltip_scopes_l_english.yml)

У `exists` и `is_same_value` аргумент `{target}` называет проверяемый объект. У `calc_true_if` параметры `{comparison}` и `{value}` берутся из `amount`, остальные дочерние записи задают проверяемые условия. Например, в `tech_fe_affluence_1` требуется выполнение как минимум четырёх условий из списка. [Игровой пример](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_fallen_empire_tech.txt:157)

| Группа | Игровые ключи |
|---|---|
| Перебор объектов | `any_agreement`, `any_country`, `any_member`, `any_neighbor_country`, `any_owned_leader`, `any_owned_nonprimary_starbase`, `any_owned_planet`, `any_owned_pop_group`, `any_owned_species`, `any_planet_within_border`, `any_relation`, `any_system_megastructure`, `any_system_planet`, `any_system_within_border` |
| Переход к другому объекту | `federation`, `founder_species`, `owner`, `owner_species`, `prev`, `solar_system`, `space_owner?`, `species`, `this` |
| Общие и составные проверки | `always`, `exists`, `is_same_value`, `calc_true_if` |

## Логика, вес и параметры

Для логических групп, ветвлений и операций опубликована **22 пары строк RU/EN**. Вместе с предметными проверками и областями действия это **137 пар**. Серверный словарь различает прямой `weight_modifier.factor`, условный `modifier.factor` и шаг вычисления внутри `script_value`. Прибавка сохраняет знак, а нулевой множитель выводится как ×0. Для И, ИЛИ, И-НЕ и ИЛИ-НЕ используются игровые строки. [Русские шаблоны](../../../localization/russian/sttv_tooltip_expressions_l_russian.yml) · [Английские шаблоны](../../../localization/english/sttv_tooltip_expressions_l_english.yml)

Четырнадцать аргументов читаются в контексте содержащей их проверки или операции. Например, `type` заполняет `{resource}` у `has_resource` и `{building}` у `num_buildings`, знак сравнения берётся из записи количества. Для `complex_trigger_modifier` формулировка об уровне советника применима к сочетанию `trigger = get_councilor_level`, `trigger_scope = owner`, `mode = add` и `parameters.type` с должностью советника. Иная форма попадает в отчёт вместе с исходным выражением. [Соответствия аргументов и операций](../sttv_server/tooltip_expressions.py)

Оставшиеся **24 ключа** участвуют в составлении выражения. Например, условный `factor = 0` означает «умножить вес на 0», а `has_resource = { type = minor_artifacts amount > 0 }` читается как одна проверка количества ресурса. Значение `type` в таком блоке — ресурс, в `num_buildings` — здание.

| Группа | Игровые ключи |
|---|---|
| Управление условиями | `if`, `else`, `limit`, `hidden_trigger` |
| Блок модификатора и вычисления | `modifier`, `factor`, `add`, `base`, `mult`, `complex_trigger_modifier` |
| Поля внутри конкретной проверки или формулы | `amount`, `count`, `country`, `disabled`, `in_construction`, `mode`, `parameters`, `resource`, `ship_category`, `starbase_size`, `trigger`, `trigger_scope`, `type`, `value` |

При составлении фраз учитывать и следующие особенности раскрытого дерева.

- **Логика.** Найдены явные `AND`, `OR`, `NOT`, `NOR`. Соседние требования подразумевают И. Сохранять вложенность и область отрицания. Для предусмотренного общим ТЗ `NAND` использовать синтетический пример. В записях встречаются знаки `=`, `<`, `>`, `>=`. Сохранять также различие между `yes` и `no`. [Логика и контекст](../../../Docs/semantics/LOGIC_AND_CONTEXT_RU.md)
- **Условия и подписи.** `hidden_trigger` содержит действующие проверки. В выбранных разделах `custom_tooltip` не встретился. Его текст и вложенные проверки различаются по существующему описанию. [Семантика подсказок](../../../Docs/semantics/TOOLTIPS_RU.md)
- **Вычисления.** Найдены 36 узлов `script_value` с учётом вложенных выражений и 28 узлов `scripted_trigger_test` со сравнением результата. В формуле `trigger = get_councilor_level` нужна подпись для уровня советника. Прямой множитель всего блока, условное умножение и прибавление показываются с исходным значением и в исходном порядке. Для динамического множителя указать формулу или известную зависимость. [Игровая формула](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/technologies/cosmic_storms_technologies_weight_modifiers.txt)

## Названия из игры

- В `prerequisites` встретились **316 различных скалярных ID технологий**. Их названия берутся по контексту `technology_name`. Так же использовать проверенные игровые ключи для происхождений, этик, традиций и других именованных объектов. Названия DLC получать тем же способом, что и в настройках игры. [Серверная локализация](TZ_LOCALIZATION_API_RU.md)
- Для `has_policy_flag` встретились `robots_outlawed`, `ai_outlawed` и `slavery_allowed`. Найти политику и вариант по `option.policy_flags` в `wiki.policies`. Для переходов `gateway`, `lgate`, `relay_bypass` и `wormhole` брать ключ названия из `wiki.bypass.name`. [Проверенные соответствия](../../loader/Docs/TZ_POLICIES_AND_BYPASS_RU.md)
- Технический флаг можно показать с полным ID, например «У империи установлен флаг `crystal_armor_1_weight`». При отсутствующей подписи сохранять тип и ID, при неоднозначном соответствии отмечать варианты в отчёте. Для неизвестной конструкции сохранять выражение с его дочерними условиями.

## Приёмка

1. Проверить на опубликованном наборе оба языка и одинаковые параметры шаблонов. При повторном обходе вывести новые или неразобранные конструкции с разделом и примером технологии. Техническое представление должно быть различимо в отчёте. Данные текущего снимка служат точкой сравнения.
2. Для `tech_titans` проверить альтернативы, DLC у ведущего игры, порог «не более 100 лет» и ×10 по соседней империи. Для `tech_mega_engineering` — обязательную технологию между двумя группами ИЛИ и общий множитель ×0,25. Для `tech_synthetic_leaders` — происхождение и признак вида «Некрофаг» как два условия множителя ×0,33.
3. Для `tech_crystal_armor_1` проверить **+5** по флагу, для `tech_storm_manipulation` — вычисляемый множитель и **×0**. Проверить названия политики и варианта для `robots_outlawed` и перехода `relay_bypass` на обоих языках. Корневой `allow`, неизвестный вложенный узел и неоднозначный флаг проверить синтетически. HTTP и отображение относятся к этапу сборки тултипа.
