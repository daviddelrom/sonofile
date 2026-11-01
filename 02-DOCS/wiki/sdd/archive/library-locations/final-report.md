---
type: archive
title: Final report — library-locations
description: What shipped, why, how it landed and where the evidence is.
tags: [sdd, archive]
timestamp: 2026-11-01T22:50:00Z
topic: sdd
slug: library-locations
---

# Final report — library-locations

**State: shipped** on 2026-11-01, through five squash-merged PRs (#1-#5). Constitution v1.0.0.

## What shipped

A Python CLI, `sonofile config`, that stores one per-user configuration: the music library folder, the `new` downloads folder and a naming template. Default template: `{Artista}/{Album}/{Artista} - {Título}`. It validates every input, asks before creating a missing folder, previews a path for a sample song and never touches a music file. It does not move or scan anything yet.

## Why

Every later feature (scan, organize) needs to know where the library is, where downloads arrive and how songs are named.

## How it landed

Option 2, pull request, because `main` is closed to direct changes (constitution principle 9). Each PR passed CI before the owner merged it.

## Evidence

- Spec: [library-locations](../../specs/library-locations.md) · Plan and tasks: [plan](../../plans/library-locations.md) · Analysis: [analysis](../../analysis/library-locations.md)
- [Verification](./verification.md): PASS, 101 tests after the last fix, coverage 100 %
- [Review](./review.md) · [Apply progress](./apply-progress.md) · [State](./state.yaml)
- Decisions: [decisions.md](../../decisions.md)

## Known limits

- Linux only was exercised. No dependency audit. Coverage is gated globally, not per changed line.
- Accepted risk: a parent folder swapped for a symlink during the creation prompt.
- `main` is not protected on GitHub, so nothing technically blocks a merge with red CI.

## Next

Organize: move songs from `new` into the library using the template. It must add the file extension, resolve path collisions and be dry-run by default (constitution 11-12).
