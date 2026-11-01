from pathlib import Path

import pytest

from sonofile import config_store
from sonofile.config_store import RawSettings
from sonofile.location_rules import LocationError
from sonofile.settings_service import SettingsError, SettingsService
from sonofile.template import DEFAULT_TEMPLATE, SAMPLE_TAGS, TemplateError


class Asker:
    def __init__(self, *answers: bool) -> None:
        self.answers = list(answers)
        self.asked: list[Path] = []

    def __call__(self, path: Path) -> bool:
        self.asked.append(path)
        return self.answers.pop(0) if self.answers else True


@pytest.fixture
def service(tmp_path: Path) -> SettingsService:
    return SettingsService(config_path=tmp_path / "cfg" / "config.toml", cwd=tmp_path)


def test_get_without_settings_returns_defaults(service: SettingsService) -> None:
    settings = service.get()
    assert settings.library is None
    assert settings.new is None
    assert settings.template == DEFAULT_TEMPLATE
    assert settings.template_is_default is True


def test_set_existing_locations_saves_and_reads_back(
    service: SettingsService, tmp_path: Path
) -> None:
    (tmp_path / "lib").mkdir()
    (tmp_path / "inbox").mkdir()
    asker = Asker()
    saved = service.set_locations(str(tmp_path / "lib"), str(tmp_path / "inbox"), asker)
    assert asker.asked == []
    assert service.get() == saved
    assert saved.library == tmp_path / "lib"
    assert saved.new == tmp_path / "inbox"


def test_relative_locations_are_stored_absolute(service: SettingsService, tmp_path: Path) -> None:
    saved = service.set_locations("lib", "inbox", Asker())
    assert saved.library == tmp_path / "lib"
    assert saved.new == tmp_path / "inbox"


def test_missing_folder_asks_and_is_created_when_confirmed(
    service: SettingsService, tmp_path: Path
) -> None:
    asker = Asker(True)
    service.set_locations(str(tmp_path / "lib"), None, asker)
    assert asker.asked == [tmp_path / "lib"]
    assert (tmp_path / "lib").is_dir()
    assert service.get().library == tmp_path / "lib"


def test_declining_creation_changes_nothing(service: SettingsService, tmp_path: Path) -> None:
    before = service.get()
    with pytest.raises(SettingsError, match="no se creó"):
        service.set_locations(str(tmp_path / "lib"), None, Asker(False))
    assert not (tmp_path / "lib").exists()
    assert service.get() == before


def test_declining_the_second_folder_creates_neither(
    service: SettingsService, tmp_path: Path
) -> None:
    with pytest.raises(SettingsError):
        service.set_locations(str(tmp_path / "lib"), str(tmp_path / "inbox"), Asker(True, False))
    assert not (tmp_path / "lib").exists()
    assert not (tmp_path / "inbox").exists()
    assert service.get().library is None


def test_identical_locations_are_rejected_without_asking(
    service: SettingsService, tmp_path: Path
) -> None:
    asker = Asker()
    with pytest.raises(LocationError):
        service.set_locations(str(tmp_path / "x"), str(tmp_path / "x"), asker)
    assert asker.asked == []
    assert not (tmp_path / "x").exists()


def test_new_location_is_checked_against_the_stored_library(
    service: SettingsService, tmp_path: Path
) -> None:
    service.set_locations(str(tmp_path / "lib"), None, Asker())
    before = service.get()
    with pytest.raises(LocationError, match="dentro"):
        service.set_locations(None, str(tmp_path / "lib" / "new"), Asker())
    assert service.get() == before


def test_invalid_location_keeps_previous_settings(service: SettingsService, tmp_path: Path) -> None:
    service.set_locations(str(tmp_path / "lib"), None, Asker())
    before = service.get()
    file = tmp_path / "song.mp3"
    file.write_text("x")
    with pytest.raises(LocationError):
        service.set_locations(str(file), None, Asker())
    assert service.get() == before


def test_setting_one_location_keeps_the_other(service: SettingsService, tmp_path: Path) -> None:
    service.set_locations(str(tmp_path / "lib"), None, Asker())
    service.set_locations(None, str(tmp_path / "inbox"), Asker())
    settings = service.get()
    assert settings.library == tmp_path / "lib"
    assert settings.new == tmp_path / "inbox"


def test_set_template_saves_and_is_no_longer_default(service: SettingsService) -> None:
    service.set_template("{Género}/{Artista} - {Título}")
    settings = service.get()
    assert settings.template == "{Género}/{Artista} - {Título}"
    assert settings.template_is_default is False


def test_setting_the_default_text_still_counts_as_chosen(service: SettingsService) -> None:
    service.set_template(DEFAULT_TEMPLATE)
    assert service.get().template_is_default is False


def test_unknown_field_is_rejected_and_old_settings_kept(service: SettingsService) -> None:
    service.set_template("{Artista}/{Título}")
    with pytest.raises(TemplateError, match="Genero"):
        service.set_template("{Genero}")
    assert service.get().template == "{Artista}/{Título}"


def test_preview_renders_the_sample_song(service: SettingsService) -> None:
    assert service.preview(DEFAULT_TEMPLATE) == "Daft Punk/Discovery/Daft Punk - One More Time"
    assert SAMPLE_TAGS["Album"] == "Discovery"


def test_preview_rejects_invalid_templates(service: SettingsService) -> None:
    with pytest.raises(TemplateError):
        service.preview("../{Artista}")


def test_preview_writes_nothing(service: SettingsService, tmp_path: Path) -> None:
    service.preview("{Artista}")
    assert service.config_path.exists() is False
    assert sorted(p.name for p in tmp_path.iterdir()) == []


def test_template_saved_by_another_run_is_read(service: SettingsService) -> None:
    config_store.save(service.config_path, RawSettings(template="{Año}/{Título}"))
    assert service.get().template == "{Año}/{Título}"
