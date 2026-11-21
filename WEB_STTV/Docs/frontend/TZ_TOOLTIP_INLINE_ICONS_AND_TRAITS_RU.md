# ТЗ. Встроенные иконки и названия черт в тултипах технологий

## Оглавление

- [Иконки в игровом тексте](#иконки-в-игровом-тексте)
- [Названия черт лидеров](#названия-черт-лидеров)
- [Приёмка](#приёмка)

## Иконки в игровом тексте

В ответах стенда по 679 базовым технологиям Stellaris v4.5.4 семь видов маркеров `£…£` встретились у 18 технологий. Названия залежей используют иконки в условиях веса. Описания сферы Дайсона и уплотнителя материи используют иконки внутри обычного предложения.

Добавить в конфиг загрузчика семь DDS из таблицы. Существующий загрузчик преобразует их в PNG и публикует с сохранением игрового пути относительно корня ресурсов. Например, для редких кристаллов получается `gfx/interface/icons/resources/rare_crystals.png`. [Конфиг загрузчика](../../config/loader_images.json) · [Правила публикации](../../src/loader/Docs/TZ_IMAGE_UPLOAD_RU.md)

| Маркер | Исходный файл относительно `gfx/interface/icons/` |
|---|---|
| `£energy£` | `resources/energy.dds` |
| `£minerals£` | `resources/minerals.dds` |
| `£rare_crystals£` | `resources/rare_crystals.dds` |
| `£exotic_gases£` | `resources/exotic_gases.dds` |
| `£volatile_motes£` | `resources/volatile_motes.dds` |
| `£sr_living_metal£` | `resources/sr_living_metal.dds` |
| `£blocker£` | `text_icons/text_icon_tile_blocker.dds` |

Для шести маркеров соответствие задано в `interface/texticons.gfx`. Для живого металла используем существующий малый DDS ресурса по указанному пути. [Редкие кристаллы](E:/SteamLibrary/steamapps/common/Stellaris/interface/texticons.gfx:478) · [Планетарное препятствие](E:/SteamLibrary/steamapps/common/Stellaris/interface/texticons.gfx:578)

Общий компонент игрового текста заменяет каждый известный маркер иконкой в той же позиции строки. Размер иконки следует размеру шрифта. Пробелы, числа и вложенная окраска сохраняются. Например, `£rare_crystals£ §Y+1§!` отображается как иконка кристаллов и жёлтое `+1`. В описании без цветовых кодов действует то же правило. Неизвестный или незакрытый маркер остаётся читаемым в исходном виде. [Игровая строка залежи](E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/megacorp_l_english.yml:2899) · [Компонент игрового текста](../../src/frontend/ui/base/GameText.tsx)

## Названия черт лидеров

Из 36 разных черт в условиях базовых технологий четыре имеют определения в `wiki.traits`, но лишены собственных строк RU и EN. Они встретились в 82 проверках веса у 53 технологий. Для каждого из четырёх игровых ID добавить строку с указанной ссылкой и римским номером в оба проектных каталога локализации. Сервер раскрывает ссылку обычным поиском в `wiki.localization` для выбранного языка. Номер подтверждён параметром `TIER` у соответствующей черты. По той же схеме игра задаёт подпись для `leader_trait_maniacal_2`. [Игровая локализация](E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/main_1_l_english.yml:4925) · [Источники локализации](../../config/parser_sources.json)

| Игровой ID | Исходная строка для обоих языков | Ожидаемый RU | Ожидаемый EN |
|---|---|---|---|
| `leader_trait_maniacal_3` | `$leader_trait_maniacal$ III` | Одержимость III | Maniacal III |
| `leader_trait_spark_of_genius_2` | `$leader_trait_spark_of_genius$ II` | Гениальность II | Spark of Genius II |
| `leader_trait_expertise_psionics_2` | `$leader_trait_expertise_psionics$ II` | Талант: псионика II | Expertise: Psionics II |
| `leader_trait_expertise_psionics_3` | `$leader_trait_expertise_psionics$ III` | Талант: псионика III | Expertise: Psionics III |

## Приёмка

1. Проверить публикацию и декодирование всех семи PNG. В браузере открыть условия `tech_mine_rare_crystals` и `tech_mountain_range`, затем описание `tech_dyson_sphere`. Сверить иконки кристаллов, препятствия и энергии, положение в строке, цвет числа и масштаб.
2. Проверить общий компонент на строке без цветовых кодов, на нескольких иконках в одной строке, при вложенной окраске и при неизвестном или незакрытом маркере.
3. Сверить ответы API для четырёх ID с таблицей на RU и EN. На том же наборе повторить проверку всех 391 вхождения `has_trait` у 98 технологий. В браузере проверить обе псионические черты у `tech_psionic_theory`, а также «Одержимость III» и «Гениальность II» у `tech_arkship_exodus_jump` при включённых DLC.

[English version](TZ_TOOLTIP_INLINE_ICONS_AND_TRAITS_EN.md)
