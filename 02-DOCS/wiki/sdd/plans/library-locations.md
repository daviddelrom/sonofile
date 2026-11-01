---
type: plan
title: Plan — library locations and naming template
description: Technical plan for the library-locations spec.
tags: [sdd, plan]
timestamp: 2026-11-01T22:30:00Z
topic: sdd
status: shipped
---

# Plan — library locations and naming template

Spec: [library-locations](../specs/library-locations.md). Constitution: v1.0.0.

## 0. Global constraints (verbatim)

- Default template: `{Artista}/{Album}/{Artista} - {Título}`.
- Template fields (closed, case-sensitive): `{Artista}`, `{ArtistaAlbum}`, `{Album}`, `{Título}`, `{Pista}`, `{Disco}`, `{Año}`, `{Género}`.
- Missing value → `Desconocido`. Characters not allowed in file names → `_` inside field values.
- Locations accept `~` and relative paths; they are stored absolute.
- No music file is ever modified by this feature (constitution 11-12).
- `ruff`, `mypy --strict`, `pytest` coverage ≥ 80 % (constitution 3-4).

## 1. Context & constraints

- Spec behaviours 1-10 and the Clarifications section.
- Constitution 1-2: Python CLI, `uv`. Constitution 7, 14: errors on stderr with non-zero exit; `--json` output.
- No code exists. The first task creates the project skeleton.

## 2. Architecture

```text
cli ──► settings_service ──► config_store (file, external)
              │
              ├──► location_rules   (pure: normalise + validate paths)
              └──► template         (pure: parse + validate + render)
```

- **cli**: parses commands, asks confirmations, prints results (text or `--json`). No rules inside.
- **settings_service**: orchestrates read, set and preview. Decides what is saved. Saves only after all validation passes.
- **location_rules** (pure): normalises a path to absolute; rejects non-folder, unwritable, identical or nested locations.
- **template** (pure): parses fields, rejects unknown fields or an unusable result, renders a path for given tags.
- **config_store** (external seam): reads and writes the single per-user settings file, atomically.

Key decision: all rules live in pure components with no file or terminal access. Only `config_store` and the folder-existence check touch the disk. That keeps nearly everything unit-testable.

**Decisions on the stack** (not fixed by the constitution; the owner approves them with this plan):

| Choice | Recommendation | Why / trade-off |
| --- | --- | --- |
| CLI framework | Typer | Typed, mypy-friendly, confirmation prompts built in. Costs one dependency. Alternative: stdlib `argparse`, no dependency but more code. |
| Config format and location | TOML in the user config dir (`platformdirs`) | Human-editable, read with stdlib `tomllib`. Write needs a small library (`tomli-w`). |
| Python version | `>=3.12` | Python 3.14 is installed here; 3.12 keeps a wider floor. |

## 3. Interfaces & contracts

```text
settings_service.get() -> Settings            # always returns; defaults filled in
Settings = { library: AbsPath | unset, new: AbsPath | unset,
             template: str, template_is_default: bool }

settings_service.set_locations(library?, new?, confirm_create) -> Saved | Rejected(reason)
  - normalises, validates, asks confirm_create(path) for each missing folder
  - declined confirmation → Rejected, nothing saved
  - atomic: either everything is saved or nothing

settings_service.set_template(text) -> Saved | Rejected(reason)
settings_service.preview(text) -> RelativePath | Rejected(reason)   # uses SAMPLE_TAGS; writes nothing
SAMPLE_TAGS = { Artista: "Daft Punk", ArtistaAlbum: "Daft Punk", Album: "Discovery",
                Título: "One More Time", Pista: 1, Disco: 1, Año: 2001, Género: "Electronic" }

config_store.load() -> RawSettings            # absent file -> empty RawSettings
config_store.save(RawSettings) -> None        # atomic: temp file + rename; old file kept on failure
RawSettings = { library?: AbsPath, new?: AbsPath, template?: str }

template.validate(text) -> Ok | Rejected(reason)
  - rejects: unknown field, empty segment, absolute result, any `..` segment
  - on an unknown field, the reason names the closest valid field
template.render(text, tags) -> RelativePath     # no extension; missing → Desconocido, bad chars → _
location_rules.normalise(path, cwd) -> AbsPath  # expands `~`, resolves relative paths against cwd
location_rules.validate(library, new) -> Ok | Rejected(reason)
```

CLI commands: `sonofile config show`, `config set-library PATH`, `config set-new PATH`, `config set-template TEXT`, `config preview TEXT`. A `--yes` flag answers the creation confirmation (spec Clarifications); `--json` gives machine-readable output.

## 4. Data model & flow

- One file with three keys: `library`, `new`, `template`. Absent `template` means the default.
- Flow for `set-library`: normalise → check against the stored `new` → if missing, ask → create → save atomically.
- Partial failure: a folder created before a later rejection stays; the settings file is untouched. Folders are created only after all validation passes, so this stays rare.

## 5. Testing strategy

| Acceptance criterion | Level | Fakes |
| --- | --- | --- |
| Save valid locations, read back | integration (service + real store) | temp directories |
| Default template shown as default | unit (service) | in-memory store |
| Missing location asks; declining changes nothing | unit (service) | confirmation callback, in-memory store |
| Identical or nested locations rejected | unit (`location_rules`) | none, pure |
| Unknown template field rejected, old settings kept | unit (`template`, service) | in-memory store |
| Preview writes nothing | integration | temp directory, assert it stays empty |
| No music file touched | integration | temp library with sample files, compare before and after |
| CLI output, `--json`, exit codes | CLI tests | Typer test runner |

Tests are written first (constitution 5). Edge cases: `~`, relative paths, a path that is a file, an unwritable folder, `Desconocido` for empty tags, `/` and `:` in values.

## 6. Sequencing

1. Project skeleton: `uv`, `pyproject.toml`, `ruff`, `mypy`, `pytest`, a CI workflow running the Definition of Done.
2. `template` (pure).
3. `location_rules` (pure).
4. `config_store`.
5. `settings_service`.
6. `cli`.
7. Docs and `decisions.md`.

Steps 2 and 3 are independent. Each step is verified before the next.

## 7. Risks

1. **Free-form templates** (medium): subtle names, such as empty segments, a leading `/` or `..`. Mitigation: `template.validate` rejects all three; tested in T003.
2. **Accents in field names** (medium): `{Título}` versus `{Titulo}` typed on another keyboard. Mitigation: keep exact names, report the closest valid field in the error message.
3. **Atomic save** (low): a crash mid-write corrupts the file. Mitigation: write to a temporary file and rename.
4. **Cross-platform paths** (low): only Linux is tested. Mitigation: use `pathlib`; note the gap.

## Open decisions

- The three stack choices in §2 are approved.
- Collisions between songs are out of scope here (organize feature).
- T001, T002 and T014 are scaffolding and docs with no test-first step; accepted by the owner.

## Tasks

Spec §N refers to the numbered behaviours (B1-B10) and acceptance criteria (AC) of the spec.
Every code task is preceded by its failing test (strict TDD, constitution 5).

| ID | [P] | Task | Done-check | Depends-on | Trace |
| --- | --- | --- | --- | --- | --- |
| T001 |  | Create the project skeleton: `pyproject.toml` (Python >=3.12, Typer, platformdirs, tomli-w; dev: ruff, mypy, pytest, pytest-cov), `src/sonofile/`, one smoke test | `uv sync` succeeds; `uv run pytest` passes 1 test | — | constitution 1-2 |
| T002 |  | Add the CI workflow running the Definition of Done | `.github/workflows/ci.yml` runs `ruff check`, `ruff format --check`, `mypy --strict src`, `pytest --cov-fail-under=80`; the same commands pass locally | T001 | constitution 3-4, DoD |
| T003 |  | Write failing tests for `template` (parse, unknown field and closest-field hint, render without extension, `Desconocido`, `_` replacement, empty segment, absolute result, `..` segment) | `uv run pytest tests/test_template.py` fails: module missing | T001 | B6, B7, B8, Clarifications (escaping, extension) |
| T004 |  | Implement `template` | T003 tests green; `mypy --strict` clean | T003 | B6, B7, B8, B9 |
| T005 | [P] | Write failing tests for `location_rules` (`~`, relative resolved against cwd, not a folder, unwritable, identical, nested) | `uv run pytest tests/test_location_rules.py` fails | T001 | B4, B5, Clarifications |
| T006 |  | Implement `location_rules` | T005 tests green | T005 | B4, B5 |
| T007 |  | Write failing tests for `config_store` (absent file, round-trip, atomic write, no template key means default) | `uv run pytest tests/test_config_store.py` fails | T001 | B1, B7 |
| T008 |  | Implement `config_store` with temp-file-and-rename writes | T007 tests green; a simulated failure mid-write leaves the old file intact | T007 | B1 |
| T009 |  | Write failing tests for `settings_service` (get, set locations with confirmation callback, declined creation, set template, preview writes nothing, rejects keep old settings) | `uv run pytest tests/test_settings_service.py` fails | T004, T006, T008 | B2, B3, B7, B8, B9, AC |
| T010 |  | Implement `settings_service` | T009 tests green | T009 | B2, B3, B7-B9 |
| T011 |  | Write failing CLI tests (`config show`, `set-library`, `set-new`, `set-template`, `preview`, `--yes`, `--json`, stderr and exit codes) | `uv run pytest tests/test_cli.py` fails | T010 | B2, B3, B9, constitution 7, 14 |
| T012 |  | Implement the CLI and the `sonofile` entry point | T011 tests green; `uv run sonofile --help` lists every command | T011 | B2, B3, B9 |
| T013 |  | Add the no-music-touched integration test over a temp library | test passes; file hashes before and after are identical | T010 | B10, AC |
| T014 |  | Document the commands in `readme.md`; append decisions to `decisions.md` | readme shows each command with an example; `decisions.md` has the stack decisions | T012 | constitution 16 |
| T015 |  | Final gate: all done-checks pass | the four commands in `config.yaml` `testing.commands.verify` exit 0 | T002, T013, T014 | spec Acceptance |

### Interfaces (for context-isolated implementers)

| Task | Consumes | Produces |
| --- | --- | --- |
| T004 | field list in §0 | `template.validate`, `template.render` (§3) |
| T006 | none | `location_rules.normalise`, `location_rules.validate` (§3) |
| T008 | none | `config_store.load`, `config_store.save`, `RawSettings` (§3) |
| T010 | T004, T006, T008 outputs | `settings_service.get`, `set_locations`, `set_template`, `preview`, `SAMPLE_TAGS`, `Settings` (§3) |
| T012 | `settings_service` | commands in §3: `config show`, `set-library`, `set-new`, `set-template`, `preview`; flags `--yes`, `--json` |

T003 and T005 are independent and can run in parallel; T005 is marked `[P]`.

## Review Workload Forecast

| Dimension | Forecast | Why |
| --- | --- | --- |
| Estimated changed lines | 700-1000 | 15 tasks, each with code and tests, plus CI and docs |
| Files / areas | about 20: package, tests, CI, config, docs | one new project |
| Review risk | medium | no data migration; the only risk is path validation |
| Suggested delivery | autochain, 3 PRs | exceeds the 400-line budget in `config.yaml` |

Suggested PR split: (1) T001-T002 skeleton and CI; (2) T003-T010 core; (3) T011-T015 CLI and docs.
