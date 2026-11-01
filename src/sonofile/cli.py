"""Command-line interface: parses commands, asks confirmations and prints results."""

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

import typer

from sonofile import __version__, config_store
from sonofile.settings_service import Settings, SettingsService

app = typer.Typer(help="Gestor automático de biblioteca musical.", no_args_is_help=True)
config_app = typer.Typer(help="Ubicaciones y plantilla de orden.", no_args_is_help=True)
app.add_typer(config_app, name="config")

JsonOption = Annotated[bool, typer.Option("--json", help="Salida legible por máquinas.")]
YesOption = Annotated[bool, typer.Option("--yes", help="Crear carpetas sin preguntar.")]


def _service() -> SettingsService:
    override = os.environ.get("SONOFILE_CONFIG")
    path = Path(override) if override else config_store.default_config_path()
    return SettingsService(config_path=path, cwd=Path.cwd())


def _fail(message: str, as_json: bool) -> typer.Exit:
    text = json.dumps({"error": message}, ensure_ascii=False) if as_json else message
    typer.echo(text, err=True)
    return typer.Exit(code=1)


def _show(settings: Settings, as_json: bool) -> None:
    if as_json:
        data = {k: str(v) if isinstance(v, Path) else v for k, v in asdict(settings).items()}
        typer.echo(json.dumps(data, ensure_ascii=False))
        return
    default = " (por defecto)" if settings.template_is_default else ""
    typer.echo(f"Biblioteca: {settings.library or 'sin definir'}")
    typer.echo(f"Carpeta new: {settings.new or 'sin definir'}")
    typer.echo(f"Plantilla: {settings.template}{default}")


def _version(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit


VersionOption = Annotated[
    bool,
    typer.Option("--version", callback=_version, is_eager=True, help="Muestra la versión."),
]


@app.callback()
def main(version: VersionOption = False) -> None:
    pass


@config_app.command("show")
def show(as_json: JsonOption = False) -> None:
    """Muestra las ubicaciones y la plantilla en uso."""
    try:
        _show(_service().get(), as_json)
    except ValueError as error:
        raise _fail(str(error), as_json) from error


def _set_locations(library: str | None, new: str | None, yes: bool, as_json: bool) -> None:
    def confirm(path: Path) -> bool:
        return yes or typer.confirm(f"{path} no existe. ¿Crearla?", err=True)

    try:
        _show(_service().set_locations(library, new, confirm), as_json)
    except ValueError as error:
        raise _fail(str(error), as_json) from error


@config_app.command("set-library")
def set_library(path: str, yes: YesOption = False, as_json: JsonOption = False) -> None:
    """Define la carpeta de la biblioteca."""
    _set_locations(path, None, yes, as_json)


@config_app.command("set-new")
def set_new(path: str, yes: YesOption = False, as_json: JsonOption = False) -> None:
    """Define la carpeta new, donde llegan las descargas."""
    _set_locations(None, path, yes, as_json)


@config_app.command("set-template")
def set_template(text: str, as_json: JsonOption = False) -> None:
    """Define la plantilla de orden, por ejemplo '{Artista}/{Album}/{Título}'."""
    try:
        _show(_service().set_template(text), as_json)
    except ValueError as error:
        raise _fail(str(error), as_json) from error


@config_app.command("preview")
def preview(text: str, as_json: JsonOption = False) -> None:
    """Muestra la ruta que tendría una canción de ejemplo, sin guardar nada."""
    try:
        path = _service().preview(text)
    except ValueError as error:
        raise _fail(str(error), as_json) from error
    if as_json:
        typer.echo(json.dumps({"template": text, "path": path}, ensure_ascii=False))
    else:
        typer.echo(path)
