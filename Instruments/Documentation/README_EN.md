# Documentation checks

## Contents

- [Usage](#usage)

## Usage

Run from the repository root

```powershell
python -B Instruments/Documentation/check_documentation.py WEB_STTV
```

Checks Markdown in the project root and at the top level of its `Docs/` directory. Prints JSON findings and returns status 1 when issues are found.
