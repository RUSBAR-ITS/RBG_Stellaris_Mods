# Technology tree fixtures

## Contents

- [Provenance and usage](#provenance-and-usage)

## Provenance and usage

The stage 16 parent-selection reference set ID is `8d7f30af6cc5a9504e6fbb0e2126edae8d18fe9a159f9969e574926ca62b5f01`. Tests read these files when comparing results.

- [report.json](report.json) contains 679 parent decisions for this snapshot.
- [expectations.json](expectations.json) contains 12 agreed control pairs for the same check.
- [unlock_evidence.json](unlock_evidence.json) contains 60 upgrade witnesses, the reference database digest in `database_sha256` and input file hashes. The frontend test compares technology and unlock pairs.

[Backend acceptance](../../../src/backend/tests/technology_tree/acceptance.py) · [Frontend test](../../frontend/realSet.test.ts)
