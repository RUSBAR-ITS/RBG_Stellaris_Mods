# Stage 11. Server tree navigation and settings

## Contents

- [Navigation](#navigation)
- [Database operations](#database-operations)
- [Game settings](#game-settings)
- [DLC names](#dlc-names)
  - [Proposed titles](#proposed-titles)
- [DLC thumbnails](#dlc-thumbnails)
- [Retiring directory mode](#retiring-directory-mode)
- [Acceptance](#acceptance)

## Navigation

**Approved specification.** This stage adapts the interface to the server tree and introduces a place for empire settings.

| Menu entry | Main view |
|---|---|
| Technology tree | Tree for the selected mode |
| System settings | Database operations tab |
| Game settings | DLC and Empire settings tabs |

Both settings screens use the same UI kit tab component. The first visit selects the first tab. Navigating between screens preserves the selected tab and draft DLC settings within the session. The language selector, theme, menu toggle, tree zoom and bottom status panel retain their current roles. [Tabs](elements/TZ_TABS_EN.md)

Choosing Technology tree explicitly opens the reference tree. On the first click or after clearing trees, the client requests the tree for the applied DLC set. Returning to an open tree reuses the result. Page load, settings navigation and changing the mode switch do not start a build.

## Database operations

Clear built trees appears only on this tab. It calls the existing `DELETE /api/trees/reference` operation. On success the client releases the open tree and shows the number of removed collections returned by the server. DLC settings survive the operation. On failure the client retains the tree and shows the reason in the status panel. The button is disabled while the request is running.

## Game settings

- **DLC.** Fetch the list from the server on the first visit. All DLCs are initially enabled. Edits accumulate until Apply. Discard changes restores the applied selection. In reference mode, successfully applying the settings updates the tree. A failed request preserves the draft for retry and the previously applied selection. In empire mode, applying DLC settings keeps the selection in the session. The next explicit reference tree open uses that selection.
- **Empire settings.** Place the Reference mode switch at the top, initially on. While on, all empire parameter inputs within the section are disabled for pointer and keyboard interaction. The switch itself and the DLC tab remain usable. Switching it off unlocks the section. Individual parameters and empire tree calculation belong to a later stage.
- **Technology tree with reference mode off.** Show “The empire tree is not implemented yet.” Hide any previously opened reference tree in this mode. Changing modes during a request must never display the result under the wrong mode.

## DLC names

The project supplies a draft Russian title for all 36 DLCs in the current catalog. Each game ID has a `sttv_<id>_name` key. For example, `dlc032` uses `sttv_dlc032_name`. Its value references `$machine_age$` and displays as “Машинный век”. English uses the game's titles. [Proposed Russian dictionary](../../localization/russian/sttv_dlc_names_l_russian.yml)

Ten of the 14 titles in the launcher dictionary `pdx_launcher/common/localisation/dlc_l_russian.yml` differ from their English counterparts. The launcher, content descriptions and game localization inform the translations. Wherever a suitable in-game title exists, the project dictionary references its key. Russian labels distinguish story packs, species packs and individual portraits. For example, the Infernals pack takes the name of its in-game species class from `INF_plural`. The proposed Vipra the Vapor title draws on the species' mist form. [Publisher description](https://store.steampowered.com/app/4241410/)

1. After approval, include the dictionary directory in the Russian preparation profile and publish it with the other localization sources through the existing loader. Each entry creates one `wiki.localization` document, for example `_id = {"language":"ru","key":"sttv_dlc032_name"}`. Existing preparation fills `selected` and `definitions`. Project keys have their own prefix and game definitions retain their original keys. Republishing reproduces the same documents. [Preparation profile](../../config/parser_sources.json)
2. Define the project key pattern for game IDs in the server's localization key configuration. The server requests Russian project names in batches using `lookup`, which also resolves embedded game references. For English the server requests the game's `localizable_name` and falls back to the catalog `name` when a translation is missing. A future DLC without a project translation uses the same game lookup in the selected language. A missing project entry or unresolved reference for any of the current 36 DLCs fails the dictionary check. [Key rules](../../src/server/config/localization_keys.json) · [Server lookup](../../src/server/sttv_server/localization.py)
3. The frontend displays `name[language]` from the server and sorts by the displayed name in the current language. Switching RU/EN preserves game IDs, the DLC selection and the tree.

### Proposed titles

| Game ID | English title | Proposed Russian title |
|---|---|---|
| `dlc001` | Symbols of Domination | Символы господства |
| `dlc002` | Arachnoid Portrait Pack | Набор портретов арахнидов |
| `dlc003` | Paradox Account Sign-up Bonus | Бонус за регистрацию учётной записи Paradox |
| `dlc004` | Plantoids Species Pack | Набор рас «Растеноиды» |
| `dlc010` | Creatures of the Void Portrait Pack | Набор портретов «Обитатели пустоты» |
| `dlc011` | Original Game Soundtrack | Оригинальная музыка Stellaris |
| `dlc012` | Leviathans Story Pack | Сюжетный набор «Левиафаны» |
| `dlc013` | Horizon Signal | Сигнал горизонта |
| `dlc014` | Utopia | Утопия |
| `dlc015` | Anniversary Portraits | Юбилейный набор портретов |
| `dlc016` | Synthetic Dawn Story Pack | Сюжетный набор «Заря синтетиков» |
| `dlc017` | Apocalypse | Апокалипсис |
| `dlc018` | Humanoids Species Pack | Набор рас «Гуманоиды» |
| `dlc019` | Distant Stars Story Pack | Сюжетный набор «Далёкие звёзды» |
| `dlc020` | MegaCorp | Мегакорпорация |
| `dlc021` | Ancient Relics Story Pack | Сюжетный набор «Древние реликвии» |
| `dlc022` | Lithoids Species Pack | Набор рас «Литоиды» |
| `dlc023` | Federations | Федерации |
| `dlc024` | Necroids Species Pack | Набор рас «Некроиды» |
| `dlc025` | Nemesis | Немезис |
| `dlc026` | Aquatics Species Pack | Набор рас «Аквоиды» |
| `dlc027` | Overlord | Сюзерен |
| `dlc028` | Toxoids Species Pack | Набор рас «Токсоиды» |
| `dlc029` | First Contact Story Pack | Сюжетный набор «Первый контакт» |
| `dlc030` | Galactic Paragons | Легенды галактики |
| `dlc031` | Astral Planes | Астральные измерения |
| `dlc032` | The Machine Age | Машинный век |
| `dlc033` | Cosmic Storms | Космические бури |
| `dlc034` | Grand Archive | Великий архив |
| `dlc035` | Rick The Cube Species Portrait | Портрет расы «Куб Рик» |
| `dlc036` | BioGenesis | Биогенез |
| `dlc037` | Shadows of the Shroud | Тени Покрова |
| `dlc038` | Infernals Species Pack | Набор рас «Термофилы» |
| `dlc039` | Stargazer Species Portrait | Портрет расы «Звездочёт» |
| `dlc040` | Nomads | Кочевники |
| `dlc042` | Vipra the Vapor Species Portrait | Портрет расы «Туманная випра» |

## DLC thumbnails

The test server returns valid PNG files for all 32 declared thumbnails. Currently `GET /api/trees/reference/dlcs` supplies `id` and `name` and the DLC row always receives `image={null}`.

Add a `thumbnail` field containing the published PNG's relative path or `null`. The server reads `thumbnail` from the matching MongoDB `dlc_descriptors` document and follows the image loader's path rule. For example, `dlc040` resolves to `dlc/dlc040_nomads/thumbnail.png`. The client uses the configured asset base URL and can display the list before opening any tree. A null path causes no image request. If one thumbnail fails to load, its row still displays the title and its switch remains usable. [Loader rule](../../src/loader/Docs/TZ_IMAGE_UPLOAD_EN.md)

## Retiring directory mode

Remove Open database set, Save report, Open reference tree and the previous clear action from the sidebar. Remove directory selection, the file worker and its controller, report export, the directory-based DLC view and requests to the old file service from the frontend. Retire dependencies, strings, configuration and tests used exclusively by those paths. Trace imports before removing shared code. The server tree uses cards, localization, field measurement, scrolling and connection rendering.

Server diagnostics come from the server log and build state in `tree_configs`, including timings and failure causes. The retired report collects browser diagnostics for local files. The status panel continues to show errors from active operations.

## Acceptance

1. Verify navigation, mouse and keyboard tab selection, RU/EN labels, draft retention across navigation and absence of tree builds on page load and while entering settings.
2. Open the reference tree through the menu, return from settings, switch reference mode off and on. Check the empire placeholder, DLC availability and the correct tree after a mode change.
3. Apply empty and partial DLC selections, discard a draft and exercise a failed apply. Switching language and mode preserves selected IDs.
4. Verify one RU document and a fully resolved project title for all 36 IDs. Compare RU/EN output for `dlc004` (“Набор рас «Растеноиды»” / “Plantoids Species Pack”), descriptorless `dlc001` and `dlc032` (“Машинный век” / “The Machine Age”). Exercise the fallback game name for an extra test DLC without a project entry. Cover the `dlc040` thumbnail, the missing `dlc001` thumbnail and a failed image request.
5. With test data exercise successful and failed clearing, double clicks and reopening the tree after success. Verify that the frontend builds after directory mode removal and that the server tree displays cards, images and connections.
