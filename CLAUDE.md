# CLAUDE.md

## What This Is

Scripting Nodes — a Blender add-on for building Blender add-ons visually through node graphs. Node graphs compile to Python modules that register as Blender add-ons.

Blender 5.0+ | GPL-3.0-or-later | `v4` branch = active dev, `main` = release

## Dev Commands

```bash
python ./scripts/dev.py              # Build, install, launch Blender ('r' rebuild, 'q' quit)
python ./scripts/build.py            # Production build → builds/*.zip
python ./scripts/build.py --validate-only
python ./scripts/test.py [-k name]   # Headless test suite (tests/), isolated Blender profile
python ./scripts/screenshot.py tests/visual/scenarios/basic.py out.png  # GUI screenshot of a scenario
uvx ruff check . && uvx ruff format .
```

Always run `scripts/test.py` after touching the core or nodes. `tests/test_nodes_compile.py` adds and chains every node and compiles the result.

Setup: `cp config.template.yaml config.yaml` and set your `BLENDER_EXECUTABLE` path.

Docs site (Fumadocs, Next.js static export) lives in `website/`. Pages are MDX in `website/content/docs/`; screenshots are generated from scenarios in `website/screenshots/` via `python ./scripts/docs_screenshots.py`. See `website/README.md`.

## Blender Python API Reference

The Blender Python API docs (bpy 5.1) are available as markdown files at `../blender-python-api/`. Use the fff MCP tools to search them:

- `mcp__fff-mcp__grep` — search doc contents (e.g. `blender-python-api/ register_class`)
- `mcp__fff-mcp__find_files` — find doc files by name (e.g. `blender-python-api/bpy.types.Object`)

Use these whenever you need to look up how anything in `bpy`, `bmesh`, `mathutils`, `gpu`, or any Blender API works. The docs cover all operators, types, properties, and methods.

Structure: `bpy/types/` (1709 files), `bpy/ops/` (78), `bpy/enum_items/` (206), `guides/` (16), `bmesh/`, `mathutils/`, `gpu/`, `freestyle/`, `standalone/` (aud, blf, bl_math).

## How It Works

All paths below are relative to `addon/scripting_nodes/src/`.

### Update pipeline (`core/`)

Node graphs → files of a regular Blender add-on in `<user scripts>/addons/<module_name>/`.

1. Anything that changes code only *requests* work: `node._generate()` → `scheduler.request_node`, `NodeTree.update()` → `request_tree`, load/undo/redo/settings/renames → `request_full`. Never compile or reload inside an RNA update callback.
2. `core/scheduler.py` flushes on a persistent timer (and in tests via `flush()`): `integrity` (init trees, unique ids, `versioning`) → `references.sync` → regenerate requested nodes in dependency order, re-queuing only nodes that read what changed → `compiler.compile_addon()` → `runtime.apply(files)`.
3. `core/compiler.py` is pure: node code → `{relpath: source}`. Shared by the live addon and export (`core/ops/export.py`, which regenerates in build mode).
4. `core/runtime.py` owns the generated folder: syntax check first, write, full disable/enable, roll back to the previous files if import/register fails. Only touches folders with its marker file.
5. Errors: `core/errors.py` (per node + addon load error), shown on nodes and in the sidebar status panel. Never stored in bpy data.

### Node System

- Base class: `nodes/base_node.py` (`ScriptingBaseNode`). Implement `on_create()` (sockets) and `generate()` (fill `code_inline` / `code_module` / `code_global` / `code_imports` / `code_register` / `code_unregister`, and `output.code` for data outputs). Call `self._generate()` from update callbacks.
- References to other nodes: declare `sn_reference_properties = {"prop": (bl_idnames...)}`; the field is stored by node id (`core/references.py`), resolve with `self.resolve_reference("prop")`.
- Categories: `nodes/categories/<snake_case>/`, folder names become add-menu labels.
- Sockets: `sockets/` — program/interface flow sockets pull downstream `code_inline`; data sockets' `.eval()` returns an expression string.
- Saved-data changes (renamed props/idnames/sockets) need a step in `core/versioning.py` (bump `DATA_VERSION`).

### Key Paths

- `core/` — scheduler, compiler, runtime, references, versioning, templates of the generated addon
- `node_tree/` — tree type, tree ops/UI
- `nodes/`, `sockets/` — node + socket types
- `settings/` — scene settings (`bpy.context.scene.sna`), preferences, sidebar panels
- `blend_data/` — RNA property indexing, fuzzy search
- `mcp_server/` — local MCP server (loopback, rejects browser requests)
- `handlers/` — load/save/undo/depsgraph handlers, msgbus, keymaps, log overlay
- `lib/` — shared utilities; must not import from other packages of the addon

### Registration

- `__init__.py` puts bundled wheels on `sys.path` if Blender didn't install them, `register()` runs `auto_load.init()` + `register()`
- `auto_load.py` discovers submodules, topologically sorts classes, registers strictly (errors aren't swallowed), unregisters in reverse and purges modules so re-enabling imports fresh code
- Wheels in `wheels/` declared in `blender_manifest.toml`

## Conventions

- Relative imports everywhere within the addon
- Version managed in `addon/scripting_nodes/blender_manifest.toml`
- Node and tree ids are short uuids, made unique again on load/duplicate (`core/integrity.py`)
- Folders: `ops/` and `ui/` subpackages; a leading underscore only marks private helper modules
- `config.yaml` is gitignored
