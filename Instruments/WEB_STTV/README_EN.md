# WEB_STTV research tools

## Contents

- [Using a snapshot](#using-a-snapshot)
- [Full test server reload](#full-test-server-reload)

## Using a snapshot

Run from the monorepo root with backend dependencies installed. Set `$variables` to the prepared set’s variables file. Its `WORK_DIR` selects the parent of `database_set/`. Substitute the actual path.

```powershell
$env:PYTHONPATH = (Resolve-Path WEB_STTV/src/backend).Path
$variables = 'TMP/WEB_STTV/variables.json'
$configuredWork = (Get-Content $variables -Raw | ConvertFrom-Json).WORK_DIR
$work = [IO.Path]::Combine((Resolve-Path WEB_STTV).Path, $configuredWork)
$tools = 'Instruments/WEB_STTV'
python -B "$tools/empire_parameters/inventory.py" --snapshot "$work/database_set" --output "$work/empire_parameters"
python -B "$tools/empire_parameters/classify.py" --output "$work/empire_parameters"
python -B "$tools/dlc/accept_stage21.py" --variables $variables --output "$work/dlc_matrix"
python -B "$tools/dlc/check_acquisition.py" --variables $variables --profiles "$work/dlc_matrix/matrix.json" --output $work
```

Run the following publication check on a test snapshot. It changes combinations in the selected set and writes `publication.json` alongside `matrix.json` for the frontend test.

```powershell
python -B "$tools/dlc/publish_acquisition.py" --variables $variables --output $work
```

## Full test server reload

From the workstation, the command below drops the named database over TLS with the Vault maintenance certificate. It checks the name against the loader network profile. Stop the API and check the prepared export first. Follow the drop with the regular loader commands `create`, `load`, `verify`, publish sprites with `upload-images` and start the API. The test HTTP proxy routes are in [serve.py](stand/serve.py).

```powershell
python Instruments/WEB_STTV/stand/drop_database.py --config WEB_STTV/config/loader.json --database wiki
```
