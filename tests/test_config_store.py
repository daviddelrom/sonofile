from pathlib import Path

import pytest

from sonofile import config_store
from sonofile.config_store import RawSettings, default_config_path


def test_absent_file_loads_empty_settings(tmp_path: Path) -> None:
    assert config_store.load(tmp_path / "config.toml") == RawSettings()


def test_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    settings = RawSettings(library=Path("/music"), new=Path("/new"), template="{Artista}/{Título}")
    config_store.save(path, settings)
    assert config_store.load(path) == settings


def test_unset_template_is_not_written(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    config_store.save(path, RawSettings(library=Path("/music")))
    assert "template" not in path.read_text()
    assert config_store.load(path).template is None


def test_save_creates_missing_parent_folders(tmp_path: Path) -> None:
    path = tmp_path / "deep" / "er" / "config.toml"
    config_store.save(path, RawSettings(library=Path("/music")))
    assert path.exists()


def test_save_replaces_previous_content(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    config_store.save(path, RawSettings(library=Path("/a"), new=Path("/b")))
    config_store.save(path, RawSettings(library=Path("/c")))
    assert config_store.load(path) == RawSettings(library=Path("/c"))


def test_save_leaves_no_temporary_files(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    config_store.save(path, RawSettings(library=Path("/a")))
    assert [p.name for p in tmp_path.iterdir()] == ["config.toml"]


def test_failed_save_keeps_the_old_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "config.toml"
    original = RawSettings(library=Path("/a"))
    config_store.save(path, original)

    def boom(*_: object, **__: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(config_store.os, "replace", boom)
    with pytest.raises(OSError, match="disk full"):
        config_store.save(path, RawSettings(library=Path("/b")))

    assert config_store.load(path) == original
    assert [p.name for p in tmp_path.iterdir()] == ["config.toml"]


def test_invalid_toml_raises_a_clear_error(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text("this is = = not toml")
    with pytest.raises(config_store.ConfigError, match="config.toml"):
        config_store.load(path)


def test_wrong_value_type_raises_a_clear_error(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text("library = 5\n")
    with pytest.raises(config_store.ConfigError, match="library"):
        config_store.load(path)


def test_default_path_is_a_toml_file_in_the_user_config_dir() -> None:
    path = default_config_path()
    assert path.name == "config.toml"
    assert "sonofile" in str(path)
