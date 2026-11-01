---
type: verification
title: Verification — library-locations — 2026-11-01
description: Evidence-backed verdict for library-locations — stack gate, task done-checks, acceptance criteria.
tags: [sdd, verification]
timestamp: 2026-11-01T22:40:00Z
topic: sdd
slug: library-locations
source_state: c3fb9a1 (clean)
---

# Verification — library-locations — 2026-11-01

Measured on `main` at `c3fb9a1`, after PRs #1, #2 and #3 were merged. Numbers come from one fresh run.

## Stack gate

Commands from `testing.commands.verify` in `config.yaml`:

- `uv run ruff check .` → PASS
- `uv run ruff format --check .` → PASS (13 files)
- `uv run mypy --strict src` → PASS (6 files)
- `uv run pytest --cov-fail-under=80` → PASS: 93 passed, coverage 100 % (floor 80 %)
- CI on GitHub (Python 3.12): green on PR #1, #2 and #3.

Control: the coverage gate can fail. Running one test file gave 0.41 % coverage and exit 1.

## Task done-checks

- [x] T001 skeleton — `uv sync` ok; smoke test passes
- [x] T002 CI — `.github/workflows/ci.yml`; runs green on GitHub
- [x] T003-T004 template — `tests/test_template.py`, 24 tests
- [x] T005-T006 location rules — `tests/test_location_rules.py`, 16 tests
- [x] T007-T008 config store — `tests/test_config_store.py`, 10 tests; a simulated failed write keeps the old file
- [x] T009-T010 settings service — `tests/test_settings_service.py`, 18 tests
- [x] T011-T012 CLI — `tests/test_cli.py`, 16 tests; `sonofile --help` run for real
- [x] T013 music untouched — `tests/test_music_untouched.py`; a mutant that writes into the library turns it red
- [x] T014 docs — `readme.md` documents every command; `decisions.md` updated
- [x] T015 final gate — the four commands above exit 0

## Acceptance criteria (spec)

All checked by running the installed CLI in a temporary folder, not only through tests.

- [x] Valid locations are saved and read back — `config show --json` returns both absolute paths
- [x] No template set shows the default, marked as default — `{Artista}/{Album}/{Artista} - {Título}` (por defecto)
- [x] A missing folder asks; declining changes nothing — exit 1, folder not created, stored library unchanged
- [x] Identical or nested locations are rejected — exit 1 with a message; nothing created
- [x] Unknown field, `..`, empty segment and absolute template are rejected, previous settings kept — four rejections, template still default
- [x] Preview shows the path and writes nothing — `2001/One More Time`; the file listing is identical before and after
- [x] No music file is modified — a hash of the music and inbox folders is identical before and after

## Capas no ejecutadas

- **HERRAMIENTA-AUSENTE** — dependency vulnerability audit: no audit tool is configured in the project, so nothing looked for vulnerable dependencies.
- **SUSTITUIDA** — mutation testing: one hand-made mutant on the untouched-music test instead of a mutation tool. It cannot detect weak assertions elsewhere.
- **SUSTITUIDA** — coverage: the global percentage gates the build. It cannot tell whether every line touched by a change is covered (`diff-cover` was not run). Here it is 100 %, so the risk is low today.
- **NO-APLICA** — UI and accessibility: the project has no UI.
- Not exercised: Windows and macOS. Only Linux was run.

## Hallazgos descartados

- ninguno. Open item accepted by the owner, not dismissed: a parent folder swapped for a symlink during the creation prompt (see `decisions.md`).

## Verdict: PASS — every gate is green and every acceptance criterion has observable proof. Next: `review`.
