# WEB_STTV loader specification. Uploading game images over SSH

## Contents

- [Command and configuration](#command-and-configuration)
- [Image selection](#image-selection)
- [Format and placement](#format-and-placement)
- [Repeat uploads and failures](#repeat-uploads-and-failures)
- [Acceptance](#acceptance)

## Command and configuration

**Approved.** A dedicated module under `WEB_STTV/src/loader/sttv_loader/` runs on demand from the Windows workstation hosting the game. It reads local sources, prepares PNGs and transfers them over SSH to Ubuntu. It runs independently of document import and works with MongoDB offline.

Run from the monorepo root

```powershell
sttv-loader upload-images --config WEB_STTV/config/loader_images.json
```

A dedicated image configuration specifies the game root, prepared DLC descriptor JSON directory, selection rules in the table below, run directory, SSH connection settings and destination root. Resolve relative local configuration paths against the configuration file. For the test VM use the existing SSH connection to `stellaris-wiki` (`192.168.1.36`) as `ansible` with host key verification. The configuration references credentials. Keep secrets out of the configuration and reports.

## Image selection

| Group | Source and selection rule | Files in the inspected installation |
| --- | --- | ---: |
| Technologies and variants | `gfx/interface/icons/technologies/*.dds`, direct children only | 864 |
| Research categories | `gfx/interface/icons/technologies/categories/category_*.dds`, direct children only | 13 |
| Research costs | Select `physics_research.dds`, `society_research.dds` and `engineering_research.dds` from `gfx/interface/icons/resources/` | 3 |
| DLC thumbnails | Read the scalar `thumbnail` from each prepared JSON descriptor under `scripts/dlc/`. Use `source.file` to locate the game descriptor and resolve the image against its directory in the game installation | 32 |
| Inline text icons | The six resource icons and the planetary blocker icon listed in `text_icons.files` | 7 |

Select all top-level technology icons. Base technologies and their variants in the inspected version reference 802 distinct files. Selecting the icon for a technology by `icon`, ID or `inherit_icon` belongs to the consumer. The `old_tech_icons` and `tech_templates` directories are outside the selection.

Each DLC retains its own path to `thumbnail.png`. A DLC catalog entry without a descriptor, or a descriptor without `thumbnail`, contributes no image. A declared thumbnail whose file is missing produces a preparation error identifying the descriptor and path. The current total is **919 distinct destination paths**. Counts in the table describe this installation and may change across game versions.

## Format and placement

The persistent destination root on the server is `/home/ansible/web-sttv/assets/`. The configuration specifies it independently of the code directory and temporary test directories. Preserve names and paths relative to the game root. Convert DDS to `.png` on the workstation while preserving dimensions and transparency. Copy an original PNG byte for byte. Example paths under the destination root:

```text
gfx/interface/icons/technologies/tech_titans.png
gfx/interface/icons/technologies/categories/category_computing.png
gfx/interface/icons/resources/physics_research.png
dlc/dlc040_nomads/thumbnail.png
```

In the inspected installation, `dlc/dlc027_overlord/thumbnail.png` contains a 280 × 160 JPEG. When preparing a declared thumbnail, the loader detects this format from the content and converts the JPEG to a PNG of the same size under the same name. The remaining 31 thumbnails are genuine PNGs and are copied byte for byte.

Check that sources are within the permitted directories, each thumbnail is within its own DLC directory and the target file is within the configured destination root. Detect different sources mapping to the same target path before transferring files. Ubuntu ownership, groups and permission modes are a separate task. The loader is given a destination already writable by the SSH user.

## Repeat uploads and failures

- Compare each prepared PNG's SHA-256 with the remote file at that path. Transfer new and changed files. Skip writes for identical content.
- Transfer a new or replacement file under a temporary name next to the target. Verify its contents and publish it by rename. After a connection loss between files, a repeat invocation checks files already published and completes the upload. Replacement is per file.
- Preserve files already present on the server that are absent from the current selection. Cleanup of persistent storage is a separate operation.
- Place files prepared for the run under `TMP/WEB_STTV/<run>/artifacts/` and the final report under that run's `reports/`. Report the destination root, selected, transferred and skipped counts by group, errors with relative paths, and elapsed time. A read, conversion or transfer failure produces a nonzero exit status.

## Acceptance

1. Use small inputs to check nonrecursive selection of technology icons, descriptor-relative thumbnail resolution, DDS dimensions and alpha preservation after conversion, and byte equality between an original PNG and its published copy.
2. For two DLCs, verify that identically named `thumbnail.png` files survive in separate directories. Cover an absent field, a missing declared file, a path outside the directory and a destination collision.
3. Run from the workstation against a dedicated writable root on the Ubuntu VM. Compare remote relative paths and SHA-256 digests against the prepared local files. The inspected installation yields 864 / 13 / 3 / 32.
4. Rerun with the same inputs and expect zero transferred files. Change one source in a test copy and verify that a single file is replaced. Interrupt a transfer, check that the previous target remains intact and verify that a retry completes successfully.
