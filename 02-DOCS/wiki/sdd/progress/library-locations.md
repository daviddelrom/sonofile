---
type: progress
title: Progress — library-locations
description: Implementation ledger for the library-locations plan.
tags: [sdd, progress]
timestamp: 2026-11-01T22:20:00Z
topic: sdd
---

# Progress — library-locations

| Task | Status | Evidence |
| --- | --- | --- |
| T001 | done | `uv sync` ok; smoke test red (ModuleNotFoundError) then green; 100 % coverage |
| T002 | done locally | `.github/workflows/ci.yml`; the four commands pass locally; CI run pending on the PR |
| T001-T002 | merged | PR #1, CI green |
| T003 | done | 20 tests red (module missing), then green |
| T004 | done | 25 tests green, 100 % coverage; ruff, format and mypy --strict clean |

Finding during T004: a tag value of `..` would have escaped the library even though the template rejects `..`. Added a red test, then fixed: dot-only values render as `Desconocido`.
| T005 | done | 16 tests red (module missing), then green |
| T006 | done | `location_rules`: normalise, validate, validate_pair; symlinks resolved before comparing |
| T007 | done | 10 tests red, then green |
| T008 | done | `config_store`: atomic temp-file + `os.replace`; failed write keeps the old file |
| T009 | done | 17 tests red, then green |
| T010 | done | `settings_service`: validates everything, asks confirmation for every missing folder, creates folders and saves only after all pass; 68 tests, 100 % coverage |

## Adversarial review of the core (2026-11-01)

Security reviewer: no findings. Correctness reviewer: 4 findings, reproduced.

| # | Finding | Outcome |
| --- | --- | --- |
| 1 | `C:\Music\{Artista}` passed as relative | fixed: drive prefixes and backslashes rejected |
| 2 | Folder created after the confirmation could follow a parent swapped for a symlink | accepted, see decisions.md |
| 3 | 256-byte segments accepted | fixed: literal segments rejected, rendered segments truncated to 255 bytes |
| 4 | Stored `template = ""` reported as chosen | fixed: blank counts as default |

75 tests green, 100 % coverage.

## PR 3 (T011-T015)

| Task | Status | Evidence |
| --- | --- | --- |
| T011 | done | 16 CLI tests red (module missing), then green |
| T012 | done | `sonofile --help` lists the commands; `preview` run from a real terminal |
| T013 | done | test passes; mutation check: writing a file into the library turns it red |
| T014 | done | `readme.md` documents every command |
| T015 | done | ruff, ruff format, mypy --strict, pytest (93 tests, 100 % coverage) all exit 0; CI result on the PR |
