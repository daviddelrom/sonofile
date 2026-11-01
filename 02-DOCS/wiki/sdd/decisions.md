## 2026-11-01 — library-locations plan
- Default template written with braces on every field: `{Artista}/{Album}/{Artista} - {Título}`. The spec's first draft read `Artista` and `Album` as literal folder names; fixed in place.
## 2026-11-01 — dot-only tag values (feature: library-locations, task: T004)
- Options: reject the song, replace with `_`, or render `Desconocido`. Chose `Desconocido`: it is the spec's rule for a missing value, and it keeps the path inside the library.

## 2026-11-01 — review findings on the core (feature: library-locations, tasks: T003-T010)
- Backslash is rejected in templates instead of being treated as a separator: `/` is the only separator, which keeps the path model the same on every system.
- Rendered segments longer than 255 bytes are truncated, not rejected: a long tag value must not make a song unmovable.
- Accepted: a parent folder swapped for a symlink between validation and creation (needs a local attacker acting during the confirmation prompt). Revisit if the tool ever runs with elevated rights or on shared folders.

## 2026-11-01 — CLI shape (feature: library-locations, tasks: T011-T012)
- Config path can be overridden with `SONOFILE_CONFIG`; this isolates tests from the real user config and helps scripts.
- In `--json` mode errors are also JSON, on stderr, so stdout stays empty on failure.
- The creation confirmation goes to stderr so stdout stays clean for `--json`.

## 2026-11-01 — review findings on the CLI (feature: library-locations, tasks: T011-T013)
- Control characters in human output are shown as `\xNN` instead of being removed: the user still sees that something odd was in the path.
- `--json` never prompts. A missing folder in JSON mode needs `--yes`: scripts must not hang on a prompt, and stdout stays empty on failure.
- Filesystem errors are reported with a fixed prefix and exit code 1; they are not a separate error class.
