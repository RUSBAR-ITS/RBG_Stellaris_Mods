# Document package format

## Contents

- [Contract](#contract)
- [Usage](#usage)

## Contract

Place `manifest.json` in the package root. The `format` field is `stellaris.documents.v1`, `collection` names the logical destination, and `documents` gives the total count. Each entry in `batches` supplies its relative `path`, `count` and `sha256`. Each `batches/<sha256>.json` contains an array of documents with their assigned `_id`. Composite identifiers retain field order.

## Usage

Install with `python -m pip install ./Instruments/Document_Package`. Producers call `write_batch` for each batch and `commit_manifest` once all batches are ready. Readers open `Package(directory)` and iterate checked batches through `batches()`. The package uses the Python standard library. [Format implementation](document_package/package.py)
