# CLAUDE.md

## What This Is

Scripting Nodes — a Blender add-on for building Blender add-ons visually through node graphs. Node graphs compile to Python modules that register as Blender add-ons.

Blender 5.0+ (compatible 4.3+) | GPL-3.0-or-later | `v4` branch = active dev, `main` = release

## Dev Commands

```bash
python ./scripts/dev.py              # Build, install, launch Blender ('r' rebuild, 'q' quit)
python ./scripts/build.py            # Production build → builds/*.zip
python ./scripts/build.py --validate-only
```

Setup: `cp config.template.yaml config.yaml` and set your `BLENDER_EXECUTABLE` path.

## Blender Python API Reference

The Blender Python API docs (bpy 5.1) are available as markdown files at `../blender-python-api/`. Use the fff MCP tools to search them:

- `mcp__fff-mcp__grep` — search doc contents (e.g. `blender-python-api/ register_class`)
- `mcp__fff-mcp__find_files` — find doc files by name (e.g. `blender-python-api/bpy.types.Object`)

Use these whenever you need to look up how anything in `bpy`, `bmesh`, `mathutils`, `gpu`, or any Blender API works. The docs cover all operators, types, properties, and methods.

Structure: `bpy/types/` (1709 files), `bpy/ops/` (78), `bpy/enum_items/` (206), `guides/` (16), `bmesh/`, `mathutils/`, `gpu/`, `freestyle/`, `standalone/` (aud, blf, bl_math).

## How It Works

### Code Generation (the core)

Node graphs → Python addon code:

1. Each node's `generate()` populates `self.code`, `self.code_global`, `self.code_register`, `self.code_unregister`
2. Code changes propagate through connected nodes
3. `src/features/node_tree/code_gen/generator.py` orchestrates tree-level module generation
4. `code_gen/watcher.py` monitors dirtiness and hot-reloads generated modules

### Node System

- Base class: `src/features/nodes/base_node.py` (`ScriptingBaseNode` extends `bpy.types.Node`)
- Categories: `src/features/nodes/categories/` — Data, Events, Logic, Program, Interface, Properties, Variables, Math, Groups
- Sockets: `src/features/sockets/` — Flow sockets (control flow) and data sockets (typed values). Each socket's `.eval()` returns a Python expression string.

### Key Paths

- `addon/scripting_nodes/src/features/node_tree/` — node tree class, code gen, UI
- `addon/scripting_nodes/src/features/settings/` — preferences, scene settings (`bpy.context.scene.sna`)
- `addon/scripting_nodes/src/features/blend_data/` — RNA property indexing, fuzzy search
- `addon/scripting_nodes/src/handlers/` — event handlers, timers, msgbus, keymaps
- `addon/scripting_nodes/src/lib/` — shared utilities

### Registration

- `__init__.py` loads bundled wheels, calls `auto_load.init()` / `.register()`
- `auto_load.py` discovers submodules, builds a dependency graph, topologically sorts for registration order
- Wheels in `wheels/` declared in `blender_manifest.toml`

## Conventions

- Relative imports everywhere within the addon
- Version managed in `addon/scripting_nodes/blender_manifest.toml`
- Node IDs are UUIDs assigned on creation
- `config.yaml` is gitignored
