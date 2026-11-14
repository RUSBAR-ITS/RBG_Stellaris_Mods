# PIF - More Secondary Zones and Building Slots

Версия мода: `1.0.0`  
Поддерживаемая версия Stellaris: `v4.3.7`  
Категория: `Gameplay`

Это PIF-compatible мод с пресетами для увеличения количества вторичных зон и вместимости зданий в зонах.

## Порядок загрузки

```txt
Planetary Infrastructure Framework
PIF - More Secondary Zones and Building Slots
Опциональный UI compatibility mod
```

Мод должен загружаться после PIF, чтобы его PIF inline-script hook-файлы заменяли стандартные PIF hook-файлы.

## Активная default-конфигурация

| Тип пресета | Активный default |
|---|---:|
| Secondary zone slots | 5 |
| Вместимость government-зоны | 24 |
| Вместимость secondary zones основного района | 12 |
| Вместимость resource / specialized zones | 24 |

## Категории пресетов

| Папка | Что меняет | Активные target-файлы |
|---|---|---|
| `_presets/01_secondary_zone_slots/` | Количество вторичных zone slots у поддерживаемых main-like районов | `common/inline_scripts/pif/districts/<district>/zone_slots.txt` |
| `_presets/02_government_zone_capacity/` | Вместимость `zone_default` | `common/scripted_variables/000_piz_01_government_zone_capacity_variables.txt` |
| `_presets/03_main_secondary_zone_capacity/` | Вместимость secondary zones основного района | `common/scripted_variables/000_piz_02_main_secondary_zone_capacity_variables.txt` |
| `_presets/04_resource_zone_capacity/` | Вместимость resource / specialized zones | `common/scripted_variables/000_piz_03_resource_zone_capacity_variables.txt` |

## Как переключить пресет

1. Открой папку мода.
2. Открой `_presets/`.
3. Выбери нужный пресет в нужной категории.
4. Скопируй папку `common` из выбранного пресета в корень мода.
5. Подтверди замену файлов.
6. Повтори для других категорий пресетов при необходимости.
7. Перезапусти игру.

Порядок копирования между разными категориями не важен, потому что они меняют разные target-файлы. Внутри одной категории активен последний скопированный пресет.

## Пример

Чтобы использовать 10 вторичных зон, 48 зданий в government-зоне, 18 зданий во вторичных зонах основного района и 24 здания в resource-зонах, скопируй в корень мода эти папки:

```txt
_presets/01_secondary_zone_slots/10_secondary_zones/common
_presets/02_government_zone_capacity/048_buildings/common
_presets/03_main_secondary_zone_capacity/018_buildings/common
_presets/04_resource_zone_capacity/024_buildings_default/common
```

## Порядок загрузки scripted variables

Пресеты вместимости намеренно лежат в файлах с префиксом `000_piz_`.

Stellaris использует первое загруженное объявление scripted variable. Файлы пресетов должны читаться раньше PIF-файла `pif_zones_building_capacity_variables.txt`, чтобы PIF-переменные уже были заняты при чтении стандартных PIF-значений.

Если в `error.log` остаются предупреждения о повторе переменных, они должны указывать на PIF-файлы. Если они указывают на `000_piz_*` файлы, значит пресет загрузился недостаточно рано.

## Поведение zone slots

Дополнительные вторичные zone slots переиспользуют существующий последний тип secondary slot:

```txt
slot_city_02
slot_habitat_02
slot_resort_02
```

Это соответствует рабочей схеме существующих модов на расширение zone slots. Дополнительные слоты наследуют обычные условия открытия повторяемого slot-типа.

## Диагностика

Если дополнительные строки зон видны в UI, но зоны нельзя выбрать, или игра продолжает вести себя как до переключения пресета, очисти кэш Stellaris и перезапусти игру:

```txt
Documents/Paradox Interactive/Stellaris/cache
```

Ручные изменения пресетов могут быть перезаписаны при обновлении Workshop-мода. Для постоянной пользовательской конфигурации лучше сделать локальную копию мода и переключать пресеты внутри неё.

## Существующие сохранения и количество вторичных зон

Изменение количества вторичных зон крайне рекомендуется использовать с новой игрой.

В существующих сохранениях уже построенные районы могут сохранять старое внутреннее состояние. В таких сейвах дополнительные позиции зон могут отображаться в интерфейсе, но выбор новых специализаций зон может работать некорректно. Это ограничение состояния уже созданных районов в сохранениях Stellaris 4.x.

Мод не рекомендует использовать сторонние save-fixer утилиты.

Чтобы вернуть поведение вторичных зон к базовому варианту PIF, удалите из этого мода папку:

```txt
common/inline_scripts/pif/districts/
```

Это отключит только переопределение количества вторичных зон. Пресеты вместимости зданий в зонах продолжат работать.

Отдельный ванильный пресет для вторичных зон намеренно не добавляется, потому что базовый PIF уже содержит ванильную схему zone slots.
