# sonofile

Gestor automático de biblioteca musical, desde la línea de comandos.

De momento guarda dos ubicaciones y una plantilla de orden. Todavía **no mueve ni toca ninguna
canción**.

## Instalación para desarrollo

Requiere Python 3.12 o superior y [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run sonofile --help
```

## Configuración

La configuración es una sola por usuario y se guarda en un archivo TOML en la carpeta de
configuración del usuario (en Linux, `~/.config/sonofile/config.toml`). La variable de entorno
`SONOFILE_CONFIG` permite usar otro archivo.

| Comando | Qué hace |
| --- | --- |
| `sonofile config show` | Muestra la biblioteca, la carpeta `new` y la plantilla en uso |
| `sonofile config set-library RUTA` | Define dónde se guardan y ordenan las canciones |
| `sonofile config set-new RUTA` | Define dónde llegan las descargas |
| `sonofile config set-template TEXTO` | Define cómo se ordenan las canciones |
| `sonofile config preview TEXTO` | Muestra la ruta de una canción de ejemplo, sin guardar nada |

Todos aceptan `--json`. `set-library` y `set-new` aceptan `--yes` para crear la carpeta sin
preguntar. Las rutas pueden usar `~` o ser relativas, y se guardan siempre como rutas absolutas.
La biblioteca y la carpeta `new` deben ser distintas y ninguna puede estar dentro de la otra.

```bash
sonofile config set-library ~/Música/Biblioteca
sonofile config set-new ~/Música/new --yes
sonofile config preview '{Género}/{Artista} - {Título}'
```

### Plantilla de orden

Por defecto: `{Artista}/{Album}/{Artista} - {Título}`.

Campos disponibles: `{Artista}`, `{ArtistaAlbum}`, `{Album}`, `{Título}`, `{Pista}`, `{Disco}`,
`{Año}` y `{Género}`.

- Se separa con `/`. No se admiten `\`, rutas absolutas, segmentos vacíos ni `..`.
- Si una canción no tiene valor para un campo, se escribe `Desconocido`.
- Los caracteres no permitidos en nombres de archivo se sustituyen por `_` dentro de los valores.
- La plantilla no incluye la extensión: la añadirá la función de ordenar.

## Desarrollo

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy --strict src
uv run pytest --cov-fail-under=80
```

El proceso de trabajo (constitución, especificación, plan y decisiones) está en
`02-DOCS/wiki/sdd/`.
