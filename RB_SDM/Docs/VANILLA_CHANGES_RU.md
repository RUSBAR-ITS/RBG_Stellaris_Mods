# RB_SDM — затронутые ванильные файлы и функции

## Оглавление

- [Состояние проекта](#состояние-проекта)
- [Источники проекта](#источники-проекта)

## Состояние проекта

В версии 0.0.1 список ванильных переопределений пуст. Решение, события, триггеры, эффекты, шаблоны и строки локализации имеют собственные имена. Мод использует следующие ресурсы оригинальной игры.

| Ресурс | Использование |
|---|---|
| `gfx/interface/icons/decisions/decision_resources.dds`, `event_administrative_work` | Значок и звук планетарного решения. |
| `interface/eventpictures.gfx` | Изображение `GFX_evt_alien_planet` в окнах меню. |
| `localisation/english/main_1_l_english.yml`, `localisation/russian/main_1_l_russian.yml` | Подписи кнопок ссылаются на `PREV`, `NEXT`, `BACK` и `CLOSE`. Переводы сверены по приоритетам репозитория. |

## Источники проекта

Пути указаны относительно каталога установленной Stellaris v4.5.4. Это материалы для сверки синтаксиса.

| Ванильный файл | Что изучалось |
|---|---|
| `common/decisions/example.txt` | Блоки видимости, разрешения, исполнения и веса ИИ у планетарного решения. |
| `common/decisions/03_crime_decisions.txt` | Условия собственной колонии и изменение веса решения для ИИ по состоянию планеты. |
| `common/inline_scripts/grand_archive/collection/stage_3_reward_option.txt` | Шаблон целого блока `option` с параметрами и условием показа. |
| `common/inline_scripts/grand_archive/collection/stage_3_reward_options_by_category.txt` | Повторное включение шаблона с разными параметрами в заданном порядке. |
| `common/inline_scripts/grand_archive/mutations/camouflage/camouflage_mutation.txt` | Подстановка параметра в путь вложенного `inline_script`. |
| `events/000_how_to_use_variables_in_script.txt` | Области переменных, счётчики, округление и вывод значения в локализации. |
