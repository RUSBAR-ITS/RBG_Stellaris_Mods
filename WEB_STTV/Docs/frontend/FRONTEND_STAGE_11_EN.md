# Stage 11. Server tree settings

## Contents

- [Using the reference tree](#using-the-reference-tree)
- [DLC catalog](#dlc-catalog)
- [Checks](#checks)

## Using the reference tree

Choose **Technology tree** to open the reference with all DLC enabled initially. Returning from settings reuses the open tree. Loading the page or navigating between tabs does not start a build. [Test site](http://192.168.1.36:5173/)

Under **Game settings → DLC**, change one or more switches and choose **Apply**. Changing tabs or languages preserves the draft. A failed request displays the reason and keeps the selection available for retry.

**Game settings → Empire settings** contains the **Reference mode** switch. It starts on and disables the empire parameter section. Turning it off unlocks the section. The empire tree is scheduled for a later stage. DLC settings are available in both modes.

Under **System settings → Database operations**, **Clear generated trees** removes the cached combinations. The status panel shows the number of removed collections. The next explicit open uses the applied DLC selection. [Specification](TZ_FRONTEND_STAGE_11_EN.md)

## DLC catalog

The server reads the catalog and descriptors from MongoDB. For Russian it builds the key `sttv_<id>_name` and resolves it through the localization lookup. For English and for future DLC without a project translation, it tries the game key and then the catalog name. The frontend receives both names and sorts by the selected language. [Russian dictionary](../../localization/russian/sttv_dlc_names_l_russian.yml) · [Server contract](../../src/server/README_EN.md#technology-tree)

`thumbnail` contains a PNG path relative to `/game-assets/` or `null`. An entry with a missing image retains its title and switch. The frontend opens the tree and retrieves card data over HTTP. The file-set importer, its worker and its report export have been removed.

## Checks

All 36 pairs of titles on the test VM matched the approved table, and all 36 Russian project keys resolved. The browser loaded all 32 declared thumbnails. Four entries have no thumbnail.

| Applied selection on the VM | Visible technologies |
|---|---:|
| All 36 DLC enabled | 678 |
| All disabled | 464 |
| The Machine Age only | 504 |

Type checking and the production build passed, together with 14 frontend unit tests, 17 browser scenarios from the workstation and 17 server tests on Ubuntu. Cards, images and connections were checked against the published tree. Controlled API responses exercised failures and repeated clicks. Server cleanup tests used a temporary collection prefix.
