import pytest

from sonofile.template import (
    DEFAULT_TEMPLATE,
    FIELDS,
    SAMPLE_TAGS,
    TemplateError,
    render,
    validate,
)

TAGS = {
    "Artista": "Daft Punk",
    "ArtistaAlbum": "Daft Punk",
    "Album": "Discovery",
    "Título": "One More Time",
    "Pista": 1,
    "Disco": 1,
    "Año": 2001,
    "Género": "Electronic",
}


def test_default_template_is_the_agreed_one() -> None:
    assert DEFAULT_TEMPLATE == "{Artista}/{Album}/{Artista} - {Título}"


def test_fields_are_the_closed_list() -> None:
    assert set(FIELDS) == set(TAGS)


def test_sample_tags_fill_every_field() -> None:
    assert set(SAMPLE_TAGS) == set(FIELDS)


def test_render_default_template_without_extension() -> None:
    assert render(DEFAULT_TEMPLATE, TAGS) == "Daft Punk/Discovery/Daft Punk - One More Time"


def test_render_numbers() -> None:
    assert render("{Año}/{Disco}-{Pista}", TAGS) == "2001/1-1"


def test_missing_value_becomes_desconocido() -> None:
    tags = {**TAGS, "Album": None}
    assert render(DEFAULT_TEMPLATE, tags) == "Daft Punk/Desconocido/Daft Punk - One More Time"


def test_absent_or_blank_value_becomes_desconocido() -> None:
    tags = {k: v for k, v in TAGS.items() if k != "Género"}
    assert render("{Género}", tags) == "Desconocido"
    assert render("{Género}", {**TAGS, "Género": "   "}) == "Desconocido"


def test_invalid_characters_in_values_are_replaced() -> None:
    tags = {**TAGS, "Artista": "AC/DC", "Título": 'Who: "Made" Who?'}
    assert render("{Artista}/{Título}", tags) == "AC_DC/Who_ _Made_ Who_"


def test_literal_text_is_kept() -> None:
    assert render("Música/{Artista}", TAGS) == "Música/Daft Punk"


def test_validate_accepts_default() -> None:
    validate(DEFAULT_TEMPLATE)


def test_unknown_field_is_rejected_and_names_the_field() -> None:
    with pytest.raises(TemplateError, match="Genero"):
        validate("{Genero}/{Título}")


def test_unknown_field_suggests_closest_valid_field() -> None:
    with pytest.raises(TemplateError, match="Título"):
        validate("{Titulo}")


def test_empty_segment_is_rejected() -> None:
    with pytest.raises(TemplateError, match="vac"):
        validate("{Artista}//{Título}")


def test_empty_template_is_rejected() -> None:
    with pytest.raises(TemplateError):
        validate("")


def test_trailing_separator_is_rejected() -> None:
    with pytest.raises(TemplateError, match="vac"):
        validate("{Artista}/")


def test_absolute_result_is_rejected() -> None:
    with pytest.raises(TemplateError, match="absoluta"):
        validate("/{Artista}/{Título}")


def test_parent_segment_is_rejected() -> None:
    with pytest.raises(TemplateError, match=r"\.\."):
        validate("../{Artista}")


def test_dot_segment_is_rejected() -> None:
    with pytest.raises(TemplateError):
        validate("./{Artista}")


def test_unbalanced_braces_are_rejected() -> None:
    with pytest.raises(TemplateError):
        validate("{Artista")
    with pytest.raises(TemplateError):
        validate("Artista}")


def test_render_validates_first() -> None:
    with pytest.raises(TemplateError):
        render("../{Artista}", TAGS)


@pytest.mark.parametrize("value", ["..", ".", "...", " .. "])
def test_dot_only_values_cannot_escape_the_library(value: str) -> None:
    tags = {**TAGS, "Artista": value}
    assert render("{Artista}/{Título}", tags) == "Desconocido/One More Time"


@pytest.mark.parametrize("text", ["C:\\Music\\{Artista}", "C:/Music/{Artista}", "c:{Artista}"])
def test_windows_absolute_templates_are_rejected(text: str) -> None:
    with pytest.raises(TemplateError, match="absoluta"):
        validate(text)


def test_backslash_is_rejected() -> None:
    with pytest.raises(TemplateError, match="barra invertida"):
        validate("{Artista}\\{Título}")


def test_overlong_literal_segment_is_rejected() -> None:
    with pytest.raises(TemplateError, match="largo"):
        validate("x" * 256)


def test_overlong_rendered_segment_is_truncated_to_255_bytes() -> None:
    tags = {**TAGS, "Título": "ñ" * 300}
    segment = render("{Título}", tags)
    assert len(segment.encode()) <= 255
    assert segment.startswith("ñ")
