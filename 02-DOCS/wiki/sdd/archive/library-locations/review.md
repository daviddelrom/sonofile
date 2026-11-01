---
type: review
title: Review — library-locations
description: Outcome of the adversarial reviews and the owner's merges.
tags: [sdd, review]
timestamp: 2026-11-01T22:50:00Z
topic: sdd
slug: library-locations
---

# Review — library-locations

Two adversarial reviews ran, each with a security and a correctness reviewer (general-purpose agents with a read-only mandate, because the dedicated refuter agents were not available).

| Review | Scope | Findings | Outcome |
| --- | --- | --- | --- |
| Core (PR 2) | template, location rules, config store, settings service | security 0; correctness 4 | 3 fixed, 1 accepted (symlink swapped during the creation prompt) |
| CLI (PR 5) | CLI and its tests | security 1; correctness 3 | all 4 fixed |

Every finding was reproduced before it was fixed, and each fix had a failing test first.

**There is no formal APPROVE verdict from a `review` run.** The owner read and merged each PR, which is the approval on record. Weak spots of the reviews: the reviewers did not list what they tried, so "no findings" is a weak signal; nothing was run on Windows or macOS; no dependency audit exists.

Open item accepted by the owner: see `decisions.md`, "review findings on the core".
