import os
from pathlib import Path

import pytest

from sonofile.location_rules import LocationError, normalise, validate, validate_pair


def test_normalise_expands_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    assert normalise("~/Music", cwd=Path("/elsewhere")) == tmp_path / "Music"


def test_normalise_resolves_relative_against_cwd(tmp_path: Path) -> None:
    assert normalise("library", cwd=tmp_path) == tmp_path / "library"


def test_normalise_keeps_absolute_paths(tmp_path: Path) -> None:
    assert normalise(str(tmp_path / "a"), cwd=Path("/elsewhere")) == tmp_path / "a"


def test_normalise_collapses_dot_segments(tmp_path: Path) -> None:
    assert normalise("a/../b", cwd=tmp_path) == tmp_path / "b"


def test_normalise_returns_absolute_path(tmp_path: Path) -> None:
    assert normalise("x", cwd=tmp_path).is_absolute()


def test_existing_writable_folder_is_valid(tmp_path: Path) -> None:
    validate(tmp_path)


def test_missing_folder_with_writable_parent_is_valid(tmp_path: Path) -> None:
    validate(tmp_path / "does-not-exist-yet")


def test_existing_file_is_rejected(tmp_path: Path) -> None:
    file = tmp_path / "song.mp3"
    file.write_text("x")
    with pytest.raises(LocationError, match="carpeta"):
        validate(file)


def test_missing_folder_under_a_file_is_rejected(tmp_path: Path) -> None:
    file = tmp_path / "song.mp3"
    file.write_text("x")
    with pytest.raises(LocationError):
        validate(file / "sub")


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores permissions")
def test_unwritable_folder_is_rejected(tmp_path: Path) -> None:
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(0o500)
    try:
        with pytest.raises(LocationError, match="escritura"):
            validate(locked)
        with pytest.raises(LocationError, match="escritura"):
            validate(locked / "new")
    finally:
        locked.chmod(0o700)


def test_distinct_locations_are_valid(tmp_path: Path) -> None:
    validate_pair(tmp_path / "library", tmp_path / "new")


def test_siblings_with_a_shared_prefix_are_not_nested(tmp_path: Path) -> None:
    validate_pair(tmp_path / "music", tmp_path / "music-new")


def test_identical_locations_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(LocationError, match="distintas"):
        validate_pair(tmp_path / "a", tmp_path / "a")


def test_new_inside_library_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(LocationError, match="dentro"):
        validate_pair(tmp_path / "library", tmp_path / "library" / "new")


def test_library_inside_new_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(LocationError, match="dentro"):
        validate_pair(tmp_path / "new" / "library", tmp_path / "new")


def test_symlink_to_the_same_folder_counts_as_identical(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real)
    with pytest.raises(LocationError):
        validate_pair(real, link)
