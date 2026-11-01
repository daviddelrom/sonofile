---
type: spec
title: Library locations and naming template
description: Configure the music library folder, the "new" downloads folder and the naming template.
tags: [sdd, spec]
timestamp: 2026-11-01T22:20:00Z
topic: sdd
status: approved
---

# Library locations and naming template

## Problem

sonofile needs to know where the user's music library lives, where new downloads arrive, and how
songs should be named and arranged inside the library. Without that, no later feature (scan,
organize) has a place to start.

## Goals

- The user defines the **library** location, where songs are stored and arranged.
- The user defines the **new** location, where downloaded music arrives.
- The user defines a **naming template** that says how songs are arranged in the library.
- With no choice made, the template is `{Artista}/{Album}/{Artista} - {Título}`.

## Out of scope

- Moving, copying or renaming any song. This feature only stores and validates the settings.
- Scanning or reading the content of either folder.

## Users

One person managing their own music library from the command line.

## Behaviour

1. **One configuration per user.** The settings apply to every use of the tool by that user.
2. **Set locations.** The user can set the library and new locations, and read them back.
3. **Missing folders.** If a location does not exist, the tool tells the user and asks before creating it. It never creates a folder without that confirmation.
4. **Invalid locations.** A location that cannot be used (it exists but is not a folder, or the user cannot write to it) is rejected with a clear message. Nothing is saved.
5. **Distinct locations.** The library and new locations must not be the same folder, and neither may be inside the other.
6. **Naming template.** The template is made of literal text, folder separators and fields.
   Available fields: artist, album artist, album, title, track number, disc number, year and genre (the closed list in Clarifications).
7. **Default template.** Until the user sets one, the default applies. Reading the configuration shows which template is in effect and whether it is the default.
8. **Template validation.** A template with an unknown field, or one that cannot produce a usable name, is rejected with a message naming the problem. Nothing is saved.
9. **Preview.** The user can see the path a sample song would get under a template, before saving it. The sample song is a fixed, built-in example, with every field filled.
10. **Safe by default.** Changing settings never touches music files (constitution principles 11-12).

## Acceptance criteria

- Setting valid library and new locations saves them, and reading returns the same values.
- With no template set, reading shows `{Artista}/{Album}/{Artista} - {Título}` marked as default.
- A non-existent location prompts for confirmation, and declining leaves the settings unchanged.
- Two identical or nested locations are rejected.
- A template with an unknown field, a `..` segment, an empty segment or an absolute result is rejected, and the previous settings stay intact.
- Previewing a template shows the resulting path for a sample song without writing anything.
- No music file is modified by any of the above.

## Clarifications (2026-11-01)

- **Missing tags:** a field with no value in the song produces `Desconocido`.
- **Invalid characters:** characters not allowed in file names are replaced by `_` inside field values.
- **Relative paths and `~`:** both are accepted for locations and always saved as an absolute path.
- **Field list (closed):** artist, album artist, album, title, track number, disc number, year, genre.
  "Similar tags" in behaviour 6 means exactly this list.
- **Relative paths** are resolved against the folder the command is run from.
- **File extension:** a template describes the path without the extension. The organize feature adds the song's own extension.
- **Escaping the library:** a template with a `..` segment is rejected, as are empty segments and absolute results.
- **`--yes`:** accepted as the way to answer the creation confirmation without a prompt (serves behaviour 3).
- **Collisions:** two songs getting the same path is out of scope here. It belongs to the organize feature.

## Recorded objection

A free-form template brings missing-tag, invalid-character and collision rules that may cost as much as the rest of the feature. The owner chose to proceed (2026-11-01).

## Next

`plan`. Before the first plan, run `sdd-init` to calibrate the technical runtime (no stack exists yet).
