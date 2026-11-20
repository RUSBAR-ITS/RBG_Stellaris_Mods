# Stellaris script research

## Contents

- [Running the tools](#running-the-tools)

## Running the tools

Run the commands from the repository root after [installing Stellaris Parser](../README_EN.md).

```powershell
$game = (Get-Content WEB_STTV/global_variables.json -Raw | ConvertFrom-Json).STELLARIS_ROOT
$tools = 'Instruments/Stellaris_Parser/tools'
foreach ($name in 'count_text','verify_frequency','audit_scalar_usage','verify_scalar_usage','audit_inline_scripts','audit_inline_payloads') {
    python -B "$tools/text_frequency/$name.py" --source $game --output TMP/WEB_STTV/text_frequency
    if ($LASTEXITCODE) { break }
}
foreach ($name in 'measure_patterns','catalog_and_verify') {
    python -B "$tools/script_patterns/$name.py" --source $game --output TMP/WEB_STTV/script_patterns
    if ($LASTEXITCODE) { break }
}
```

For a mod, pass its root as `--source`. Each group shares its output directory across its commands. Checks compare the AST with tokens, the lists with the current run’s manifest, and hashes with source files. WEB_STTV research reports document historical comparisons between passes 2–4. To compare results from the same corpus against a previous pass before variable filtering, pass its output directory to the frequency and scalar checks with `--reference`. The inline audit accepts a previous call inventory JSON via the same option.
