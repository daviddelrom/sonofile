"""Naming template: parse, validate and render the library path of a song."""

import difflib
import re
from collections.abc import Mapping

DEFAULT_TEMPLATE = "{Artista}/{Album}/{Artista} - {Título}"
FIELDS = ("Artista", "ArtistaAlbum", "Album", "Título", "Pista", "Disco", "Año", "Género")
MISSING = "Desconocido"

SAMPLE_TAGS: dict[str, str | int] = {
    "Artista": "Daft Punk",
    "ArtistaAlbum": "Daft Punk",
    "Album": "Discovery",
    "Título": "One More Time",
    "Pista": 1,
    "Disco": 1,
    "Año": 2001,
    "Género": "Electronic",
}

_FIELD = re.compile(r"\{([^{}]*)\}")
_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


class TemplateError(ValueError):
    """The template cannot be used."""


def validate(template: str) -> None:
    if not template.strip():
        raise TemplateError("La plantilla está vacía.")
    if template.startswith(("/", "\\")):
        raise TemplateError("La plantilla no puede ser una ruta absoluta.")

    remainder = _FIELD.sub("", template)
    if "{" in remainder or "}" in remainder:
        raise TemplateError("Las llaves de la plantilla no están equilibradas.")

    for name in _FIELD.findall(template):
        if name not in FIELDS:
            hint = difflib.get_close_matches(name, FIELDS, n=1, cutoff=0.6)
            suggestion = f" ¿Quisiste decir {{{hint[0]}}}?" if hint else ""
            raise TemplateError(f"Campo desconocido: {{{name}}}.{suggestion}")

    for segment in template.split("/"):
        if not segment.strip():
            raise TemplateError("La plantilla tiene un segmento vacío.")
        if segment in {".", ".."}:
            raise TemplateError("La plantilla no puede contener segmentos '.' ni '..'.")


def render(template: str, tags: Mapping[str, str | int | None]) -> str:
    validate(template)

    def replace(match: re.Match[str]) -> str:
        value = tags.get(match.group(1))
        text = "" if value is None else str(value).strip()
        if not text.strip("."):
            return MISSING
        return _INVALID_CHARS.sub("_", text)

    return _FIELD.sub(replace, template)
