import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from sonofile.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    config = tmp_path / "cfg" / "config.toml"
    monkeypatch.setenv("SONOFILE_CONFIG", str(config))
    monkeypatch.chdir(tmp_path)
    return config


def test_help_lists_every_command() -> None:
    result = runner.invoke(app, ["config", "--help"])
    assert result.exit_code == 0
    for command in ("show", "set-library", "set-new", "set-template", "preview"):
        assert command in result.output


def test_show_without_settings_shows_defaults() -> None:
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "{Artista}/{Album}/{Artista} - {Título}" in result.output
    assert "por defecto" in result.output


def test_show_json_is_machine_readable() -> None:
    result = runner.invoke(app, ["config", "show", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "library": None,
        "new": None,
        "template": "{Artista}/{Album}/{Artista} - {Título}",
        "template_is_default": True,
    }


def test_set_library_with_existing_folder(tmp_path: Path) -> None:
    (tmp_path / "lib").mkdir()
    result = runner.invoke(app, ["config", "set-library", "lib"])
    assert result.exit_code == 0
    shown = json.loads(runner.invoke(app, ["config", "show", "--json"]).output)
    assert shown["library"] == str(tmp_path / "lib")


def test_missing_folder_prompts_and_creates_on_yes(tmp_path: Path) -> None:
    result = runner.invoke(app, ["config", "set-library", "lib"], input="y\n")
    assert result.exit_code == 0
    assert (tmp_path / "lib").is_dir()


def test_missing_folder_declined_changes_nothing(tmp_path: Path) -> None:
    result = runner.invoke(app, ["config", "set-library", "lib"], input="n\n")
    assert result.exit_code != 0
    assert not (tmp_path / "lib").exists()
    assert json.loads(runner.invoke(app, ["config", "show", "--json"]).output)["library"] is None


def test_yes_flag_skips_the_prompt(tmp_path: Path) -> None:
    result = runner.invoke(app, ["config", "set-new", "inbox", "--yes"])
    assert result.exit_code == 0
    assert (tmp_path / "inbox").is_dir()


def test_nested_locations_fail_with_message_on_stderr(tmp_path: Path) -> None:
    runner.invoke(app, ["config", "set-library", "lib", "--yes"])
    result = runner.invoke(app, ["config", "set-new", "lib/new", "--yes"])
    assert result.exit_code == 1
    assert "dentro" in result.stderr
    assert result.stdout == ""


def test_set_template_then_show() -> None:
    result = runner.invoke(app, ["config", "set-template", "{Género}/{Título}"])
    assert result.exit_code == 0
    shown = json.loads(runner.invoke(app, ["config", "show", "--json"]).output)
    assert shown["template"] == "{Género}/{Título}"
    assert shown["template_is_default"] is False


def test_unknown_field_is_rejected_with_exit_code_1() -> None:
    result = runner.invoke(app, ["config", "set-template", "{Genero}"])
    assert result.exit_code == 1
    assert "Genero" in result.stderr


def test_preview_prints_the_sample_path_and_writes_nothing(isolated_config: Path) -> None:
    result = runner.invoke(app, ["config", "preview", "{Artista}/{Título}"])
    assert result.exit_code == 0
    assert "Daft Punk/One More Time" in result.output
    assert not isolated_config.exists()


def test_preview_json() -> None:
    result = runner.invoke(app, ["config", "preview", "{Año}", "--json"])
    assert json.loads(result.output) == {"template": "{Año}", "path": "2001"}


def test_preview_rejects_invalid_template() -> None:
    result = runner.invoke(app, ["config", "preview", "../{Artista}"])
    assert result.exit_code == 1
    assert ".." in result.stderr


def test_errors_in_json_mode_are_json_on_stderr() -> None:
    result = runner.invoke(app, ["config", "preview", "{Nada}", "--json"])
    assert result.exit_code == 1
    assert "error" in json.loads(result.stderr)


def test_broken_config_file_is_a_clean_error(isolated_config: Path) -> None:
    isolated_config.parent.mkdir(parents=True)
    isolated_config.write_text("not = = toml")
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 1
    assert "config" in result.stderr.lower()


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
