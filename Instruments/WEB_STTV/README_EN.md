# WEB_STTV research tools

## Contents

- [Using a snapshot](#using-a-snapshot)

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
