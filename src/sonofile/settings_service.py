"""Orchestrates reading, changing and previewing the user's settings."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from sonofile import config_store, location_rules, template
from sonofile.config_store import RawSettings


class SettingsError(ValueError):
    """A change was not applied."""


@dataclass(frozen=True)
class Settings:
    library: Path | None
    new: Path | None
    template: str
    template_is_default: bool


class SettingsService:
    def __init__(self, config_path: Path, cwd: Path) -> None:
        self.config_path = config_path
        self.cwd = cwd

    def get(self) -> Settings:
        return _build(config_store.load(self.config_path))

    def set_locations(
        self,
        library: str | None,
        new: str | None,
        confirm_create: Callable[[Path], bool],
    ) -> Settings:
        raw = config_store.load(self.config_path)
        target_library = location_rules.normalise(library, self.cwd) if library else raw.library
        target_new = location_rules.normalise(new, self.cwd) if new else raw.new

        changed = [p for p in (library and target_library, new and target_new) if p]
        for path in changed:
            location_rules.validate(path)
        if target_library and target_new:
            location_rules.validate_pair(target_library, target_new)

        missing = [p for p in changed if not p.exists()]
        for path in missing:
            if not confirm_create(path):
                raise SettingsError(f"No se guardó nada: no se creó {path}.")

        for path in missing:
            path.mkdir(parents=True, exist_ok=True)
        updated = RawSettings(library=target_library, new=target_new, template=raw.template)
        config_store.save(self.config_path, updated)
        return _build(updated)

    def set_template(self, text: str) -> Settings:
        template.validate(text)
        raw = config_store.load(self.config_path)
        updated = RawSettings(library=raw.library, new=raw.new, template=text)
        config_store.save(self.config_path, updated)
        return _build(updated)

    def preview(self, text: str) -> str:
        return template.render(text, template.SAMPLE_TAGS)


def _build(raw: RawSettings) -> Settings:
    return Settings(
        library=raw.library,
        new=raw.new,
        template=raw.template or template.DEFAULT_TEMPLATE,
        template_is_default=raw.template is None,
    )
