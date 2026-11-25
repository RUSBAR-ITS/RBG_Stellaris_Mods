# UIOD_RUS — затронутые ванильные файлы и функции

## Оглавление

- [Версия 0.0.4](#версия-004)
- [Версия 0.0.3](#версия-003)
- [Переопределяемые строки модов](#переопределяемые-строки-модов)

## Версия 0.0.4

- `common/scripted_effects/psionic_auras_scripted_effects.txt` (Stellaris 4.6.0). Заплатка переопределяет `desire_aura_max_intensity_effect` через одноимённый файл сабмода `common/scripted_effects/uiod_psionic_auras_scripted_effects.txt`. Для планет и ковчегов предел берётся из `uiod_ascension_limit`, следующий уровень — из собственного значения `uiod_rus_next_ascension_tier`.
- `common/script_values/01_script_values_paragon.txt`. Ванильная формула `add_planet_ascension_tier` служит основой для сравнения. Другие её вызовы используют оригинал. Системный интервал срабатывания остаётся задан в `common/inline_scripts/shroud/psionic_aura_definition.txt`.
- `common/technology/ui_tech_ascension_theory_repeatable.txt` принадлежит Ascension Slots. UIOD_RUS замещает этот файл и удаляет отклоняемое поле `ai_update_type`. Источник технологии и переменной лимита — сабмод `1890399946`.

## Версия 0.0.3

Затронутых ванильных файлов, функций и ключей локализации нет. Игровые определения, интерфейсы и механики ванильной игры не переопределяются.

Ванильная английская локализация и подготовленные русские тексты используются только как справочные источники терминологии. Ссылки на них сохраняются в общем глоссарии.

## Переопределяемые строки модов

| Источник | Исходный русский файл | Количество ключей |
| --- | --- | ---: |
| UI Overhaul Dynamic (`1623423360`) | `localisation/ui_overhaul_qhd_l_russian.yml` | 12 |
| UI Overhaul Dynamic - Ascension Slots (`1890399946`) | `localisation/ui_overhaul_qhd-technology_l_russian.yml` | 7 |

Полный список ключей и утверждённых переводов приведён в [ТЗ](TZ_RU.md#6-утверждённые-переводы). Переопределения хранятся в собственных файлах UIOD_RUS; оригиналы Workshop не изменяются.
