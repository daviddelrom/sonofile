import hashlib
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from sonofile.cli import app

runner = CliRunner()


def snapshot(root: Path) -> dict[str, tuple[str, int]]:
    return {
        str(p.relative_to(root)): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


@pytest.fixture
def library(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "music"
    (root / "Artista" / "Album").mkdir(parents=True)
    (root / "Artista" / "Album" / "a.mp3").write_bytes(b"ID3-one")
    (root / "b.flac").write_bytes(b"fLaC-two")
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "c.mp3").write_bytes(b"ID3-three")
    monkeypatch.setenv("SONOFILE_CONFIG", str(tmp_path / "cfg" / "config.toml"))
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_every_config_command_leaves_music_files_untouched(library: Path) -> None:
    music, inbox = library / "music", library / "inbox"
    before = {"music": snapshot(music), "inbox": snapshot(inbox)}
    assert before["music"] and before["inbox"]

    commands = [
        (["config", "set-library", str(music)], 0),
        (["config", "set-new", str(inbox)], 0),
        (["config", "set-template", "{Género}/{Artista} - {Título}"], 0),
        (["config", "preview", "{Artista}/{Título}"], 0),
        (["config", "show"], 0),
        (["config", "show", "--json"], 0),
        (["config", "set-library", str(inbox)], 1),
        (["config", "set-template", "{Nada}"], 1),
    ]
    for command, expected_exit in commands:
        assert runner.invoke(app, command).exit_code == expected_exit, command

    assert {"music": snapshot(music), "inbox": snapshot(inbox)} == before
    shown = json.loads(runner.invoke(app, ["config", "show", "--json"]).output)
    assert shown["library"] == str(music)


def test_pointing_the_library_at_a_folder_with_music_adds_no_files(library: Path) -> None:
    music = library / "music"
    names = sorted(p.name for p in music.rglob("*"))
    runner.invoke(app, ["config", "set-library", str(music)])
    assert sorted(p.name for p in music.rglob("*")) == names
