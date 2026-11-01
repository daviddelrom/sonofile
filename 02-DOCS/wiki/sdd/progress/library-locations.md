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
