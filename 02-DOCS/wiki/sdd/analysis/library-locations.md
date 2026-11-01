---
type: analysis
title: Analysis — library-locations
description: Pre-implementation consistency report across constitution, spec, plan and tasks.
tags: [sdd, analysis]
timestamp: 2026-11-01T22:40:00Z
topic: sdd
---

# Analysis — library-locations

Inputs: [constitution v1.0.0](../constitution.md), [spec](../specs/library-locations.md), [plan and tasks](../plans/library-locations.md).

**GATE: PASS** — 0 CRITICAL, 0 HIGH, 5 MEDIUM, 4 LOW.

## Coverage map

| REQ | Spec requirement | Plan section | Tasks | Status |
| --- | --- | --- | --- | --- |
| B1 | One configuration per user | §2, §4 | T007, T008 | covered |
| B2 | Set and read locations | §3 | T009-T012 | covered |
| B3 | Missing folder: ask before creating | §3, §4 | T009, T010, T012 | covered |
| B4 | Invalid location rejected | §2, §3 | T005, T006 | covered |
| B5 | Distinct, non-nested locations | §2 | T005, T006 | covered |
| B6 | Template with closed field list | §0, §2 | T003, T004 | covered |
| B7 | Default template, shown as default | §3, §4 | T007, T009, T010 | covered |
| B8 | Template validation | §2, §7 | T003, T004, T009 | AMBIGUOUS (finding 1) |
| B9 | Preview without writing | §3 | T009-T012 | AMBIGUOUS (finding 2) |
| B10 | Music files untouched | §0 | T013 | covered |
| — | `--yes` flag | §3 | T011, T012 | DRIFT, minor (finding 8) |

Constitution 3-5, 7, 11-12, 14 and 16 are all honoured. No contradiction and no duplication found.

## Findings

| # | Severity | Type | Where | Conflict | Resolve in |
| --- | --- | --- | --- | --- | --- |
| 1 | MEDIUM | Gap | spec B8, plan §7 risk 1, T003 | The plan rejects empty segments and absolute results, but not `..` segments. A template like `../{Artista}` would point outside the library. | plan, tasks (add to T003) |
| 2 | MEDIUM | Ambiguity | plan §3 `preview(text, sample_tags)`, T011 | The CLI command is `preview TEXT` and gives no sample tags. Who supplies the sample song is undefined. | plan |
| 3 | MEDIUM | Ambiguity | plan §3 | `config_store` has no contract, and `template`/`location_rules` signatures are partial. No task has an Interfaces block, so T009 would depend on prose. | plan, tasks |
| 4 | MEDIUM | Ambiguity | spec B6, plan `template.render` | The rendered path has no file extension. It is not stated that organize adds it. | clarify, plan |
| 5 | MEDIUM | Ambiguity | spec Clarifications | Relative paths are resolved against what? Presumably the current directory; not written. | clarify |
| 6 | LOW | Wording | spec B6 | "and similar tags" is superseded by the closed list in Clarifications. | clarify |
| 7 | LOW | Wording | plan §4 | "four keys" but three are listed. | plan |
| 8 | LOW | Drift | plan §3, T011-T012 | `--yes` is not in the spec; it serves B3 in non-interactive use. Accept or cut. | owner |
| 9 | LOW | Process | T001, T002, T014 | These have no failing-test step (constitution 5). They are scaffolding and docs. Accept. | owner |

## Recommended routing

- **plan / tasks:** findings 1, 2, 3, 7.
- **clarify:** findings 4, 5, 6.
- **owner decision:** findings 8, 9.

None blocks `implement`. Findings 1 and 3 are worth fixing first: the first is a safety gap and the second affects the isolated implementers.
