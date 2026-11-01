## 2026-11-01 — library-locations plan
- Default template written with braces on every field: `{Artista}/{Album}/{Artista} - {Título}`. The spec's first draft read `Artista` and `Album` as literal folder names; fixed in place.
## 2026-11-01 — dot-only tag values (feature: library-locations, task: T004)
- Options: reject the song, replace with `_`, or render `Desconocido`. Chose `Desconocido`: it is the spec's rule for a missing value, and it keeps the path inside the library.
