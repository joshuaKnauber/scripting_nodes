# Scripting Nodes (Serpens)

Build Blender add-ons visually. Node trees compile to a regular Python add-on that is
reloaded live while you edit, and can be exported as an installable extension.

Requires Blender 5.0+. Licensed GPL-3.0-or-later.

## Development

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp config.template.yaml config.yaml               # set BLENDER_EXECUTABLE
```

| Command | What it does |
| --- | --- |
| `python scripts/dev.py` | Build + install the extension, launch Blender (`r` restart, `q` quit) |
| `python scripts/test.py` | Run the headless test suite in Blender (`-k name` to filter, `-v` verbose) |
| `python scripts/screenshot.py <scenario> out.png` | Open the GUI on a scenario from `tests/visual/scenarios/` and save a screenshot |
| `python scripts/build.py` | Production build into `builds/` |
| `uvx ruff check . && uvx ruff format .` | Lint and format |

Tests and screenshots run Blender with a throwaway user profile, so they never touch your
own preferences, extensions or generated add-ons.

## Layout

```
addon/scripting_nodes/      the extension (blender_manifest.toml, wheels/)
  src/core/                 update pipeline: scheduler, compiler, runtime, versioning
  src/nodes/                node base class + node categories
  src/sockets/              socket types and type conversions
  src/node_tree/            the node tree type and its UI
  src/settings/             scene settings, preferences, sidebar panels
  src/handlers/             load/save/undo handlers, keymaps, log overlay
  src/mcp_server/           optional local MCP server
tests/                      headless tests (run inside Blender), visual scenarios
scripts/                    dev, build, test and screenshot tools
website/                    documentation site
```

See [CLAUDE.md](CLAUDE.md) for how the update pipeline and the node API work.
