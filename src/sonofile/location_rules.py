"""Rules for the library and new-downloads locations. Pure: only reads the disk."""

import os
from pathlib import Path


class LocationError(ValueError):
    """The location cannot be used."""


def normalise(path: str | Path, cwd: Path) -> Path:
    expanded = Path(path).expanduser()
    return (cwd / expanded).resolve()


def validate(path: Path) -> None:
    resolved = path.resolve()
    if resolved.exists():
        if not resolved.is_dir():
            raise LocationError(f"{path} existe pero no es una carpeta.")
        _require_writable(resolved, path)
        return

    ancestor = next(p for p in resolved.parents if p.exists())
    if not ancestor.is_dir():
        raise LocationError(f"{ancestor} no es una carpeta, no se puede crear {path}.")
    _require_writable(ancestor, path)


def validate_pair(library: Path, new: Path) -> None:
    lib, new_ = library.resolve(), new.resolve()
    if lib == new_:
        raise LocationError("La biblioteca y la carpeta new deben ser carpetas distintas.")
    if new_.is_relative_to(lib):
        raise LocationError("La carpeta new no puede estar dentro de la biblioteca.")
    if lib.is_relative_to(new_):
        raise LocationError("La biblioteca no puede estar dentro de la carpeta new.")


def _require_writable(folder: Path, shown: Path) -> None:
    if not os.access(folder, os.W_OK | os.X_OK):
        raise LocationError(f"No hay permiso de escritura para {shown}.")
