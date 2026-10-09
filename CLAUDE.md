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

Always run `scripts/test.py` after touching the core or nodes. `tests/test_nodes_compile.py` adds and chains every node, compiles and loads the result.

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

Developer docs (read before changing the core or writing nodes): `website/content/docs/development/` — `architecture.mdx`, `writing-nodes.mdx`, `context-reference.mdx`, `testing.mdx`.

### Update pipeline (`core/`)

Node graphs → files of a regular Blender add-on in `<user scripts>/addons/<module_name>/`. Nodes store **no** generated code; every rebuild compiles the graph again.

1. Changes only *request* a rebuild (`node.mark_dirty()`, `NodeTree.update()`, load/undo/settings → `scheduler.request_*`). Never compile or reload inside an RNA update callback.
2. `core/scheduler.py` flushes on a timer (tests: `flush()`): integrity (ids, versioning) → sync sockets → references → `compiler.compile_addon()` → `runtime.apply(files)`.
3. `core/compiler.py` + `core/context.py`: root nodes emit at module level, flow nodes when reached, value nodes when their output is used. Every line knows its node (errors, code preview).
4. `core/runtime.py`: syntax check, write, full disable/enable, roll back on failure. Only touches folders with its marker file.
5. Errors: `core/errors.py`; `emit()` errors, load errors and runtime errors (`core/tracebacks.py`, via `sys.excepthook`) all show on the node.
6. Dev vs export differences only in `core/helpers.py`.

### Node System

- `nodes/base_node.py` `ScriptingBaseNode`: declare sockets (`sn_inputs`/`sn_outputs` or `socket_specs()`, helpers in `sockets/spec.py`), implement `emit(ctx)`. Properties rebuild automatically (no `update=`).
- Write code with templates: `ctx.code(f"""...{ctx.flow("next")}...""")`; values with `ctx.output(key, expr)`; inputs with `ctx.input(key)`; module code with `ctx.module`; `raise NodeError(...)` for incomplete setups.
- One flow socket type (`ScriptingFlowSocket`) with `kind` PROGRAM/LOGIC/INTERFACE (color + compatibility).
- Names in the generated code: declared in `sn_names()` (`core/naming.py`: `Class`, `Idname`, `Symbol`), read with `ctx.name(key)` / `node.sn_name(key)`; readable, from labels, suffix only on collision. Locals via `ctx.var()`.
- References to other nodes: `sn_reference_properties`, stored by node id (`core/references.py`); cross-tree names via `ctx.symbol`.
- Functions (node groups): the tree interface (`tree.interface`, sidebar Group tab) is the source of truth; Blender's Group Input / Output nodes, interface socket classes in `sockets/interface.py`, compiled in `core/functions.py` + `compiler._group_function`. Make Group / Ungroup are our own operators (Blender's only run in built-in trees).
- Shared bases: `PropertyNode`, `PropertyFieldNode`, `ClassBodyContainerMixin`, `PropertyTargetMixin`, `OperatorCallMixin`, `event_node()`.
- Saved-data changes need a step in `core/versioning.py`; socket changes don't (re-synced from declarations).

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
