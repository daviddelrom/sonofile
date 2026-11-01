"""Reads and writes the single per-user settings file (TOML), atomically."""

import os
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path

import platformdirs
import tomli_w


class ConfigError(ValueError):
    """The settings file cannot be read."""


@dataclass(frozen=True)
class RawSettings:
    library: Path | None = None
    new: Path | None = None
    template: str | None = None


def default_config_path() -> Path:
    return Path(platformdirs.user_config_dir("sonofile")) / "config.toml"


def load(path: Path) -> RawSettings:
    if not path.exists():
        return RawSettings()
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"No se puede leer {path}: {error}") from error

    values: dict[str, str | None] = {}
    for key in ("library", "new", "template"):
        value = data.get(key)
        if value is not None and not isinstance(value, str):
            raise ConfigError(f"En {path}, '{key}' debe ser texto.")
        values[key] = value
    return RawSettings(
        library=Path(values["library"]) if values["library"] else None,
        new=Path(values["new"]) if values["new"] else None,
        template=values["template"],
    )


def save(path: Path, settings: RawSettings) -> None:
    data: dict[str, str] = {}
    if settings.library is not None:
        data["library"] = str(settings.library)
    if settings.new is not None:
        data["new"] = str(settings.new)
    if settings.template is not None:
        data["template"] = settings.template

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(dir=path.parent, prefix=".config-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            tomli_w.dump(data, handle)
        os.replace(temp_name, path)
    except BaseException:
        Path(temp_name).unlink(missing_ok=True)
        raise
