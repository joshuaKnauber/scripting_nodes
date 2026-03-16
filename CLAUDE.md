# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Scripting Nodes is a Blender add-on that lets users build Blender add-ons visually through node graphs. Node graphs are compiled into Python modules that register as Blender add-ons. The project has two parts: the Blender add-on (`addon/scripting_nodes/`) and a documentation site (`docs/`).

**Target:** Blender 5.0.0+ (compatible with 4.3+) | **License:** GPL-3.0-or-later | **Branch:** `v4` is active development, `main` is release.

## Development Commands

### Setup
```bash
cp config.template.yaml config.yaml   # Set BLENDER_EXECUTABLE path
pip install -r requirements.txt        # fake-bpy-module-latest, pyyaml, psutil, colorama
```

### Addon Development
```bash
python ./scripts/dev.py    # Build, install extension to Blender, launch Blender
                           # Press 'r' to rebuild+relaunch, 'q' to quit
python ./scripts/build.py                # Production build → builds/*.zip
python ./scripts/build.py -v 4.0.1      # Build with specific version
python ./scripts/build.py --validate-only
```

### Documentation Site
```bash
cd docs && npm install
npm run dev          # Dev server
npm run build        # Production build
npm run types:check  # TypeScript type checking
```

## Architecture

### Add-on Entry & Registration
- `addon/scripting_nodes/__init__.py` — Entry point; loads bundled wheels, calls `auto_load.init()` / `.register()`
- `auto_load.py` — Recursively discovers all submodules, builds a dependency graph of Blender classes, and topologically sorts them for registration order

### Code Generation Pipeline
The core feature: node graphs → Python addon code.

1. **Per-node generation:** Each node's `generate()` populates `self.code`, `self.code_global`, `self.code_register`, `self.code_unregister`
2. **Propagation:** When a node's code changes, it triggers regeneration on connected nodes
3. **Tree-level:** `src/features/node_tree/code_gen/generator.py` orchestrates folder structure and per-tree module files
4. **Hot-reload:** `code_gen/watcher.py` monitors dirtiness flags and dynamically reloads generated modules

### Node System
- **Base class:** `src/features/nodes/base_node.py` (`ScriptingBaseNode` extends `bpy.types.Node`)
- **Categories:** `src/features/nodes/categories/` — Data, Logic, Program, Interface, Properties, Variables, Math, Groups
- **Sockets:** `src/features/sockets/` — Flow sockets (control flow) and data sockets (typed values). Each socket has `.eval()` returning a Python expression string.

### Key Directories
- `src/features/node_tree/` — `ScriptingNodeTree` class, code generation, UI panels/operators
- `src/features/settings/` — Addon preferences, scene settings (`bpy.context.scene.sna`), UI settings
- `src/features/ai/` — AI integration (OpenAI/OpenRouter streaming via httpx)
- `src/features/blend_data/` — RNA property indexing and fuzzy search
- `src/handlers/` — Blender event handlers, timers, msgbus subscriptions, keymaps
- `src/lib/` — Shared utilities (code formatting, node tree helpers, socket traversal, logging)

### Bundled Dependencies
Wheels in `addon/scripting_nodes/wheels/` are declared in `blender_manifest.toml`. Includes httpx, autopep8, and their transitive deps. `__init__.py` ensures they're loadable at startup.

## Conventions

- All imports within the addon use relative imports
- Version is managed in `addon/scripting_nodes/blender_manifest.toml`
- Node IDs are UUIDs assigned on creation for tracking
- `config.yaml` is gitignored; `config.template.yaml` is the reference
- The dev script builds a proper Blender extension zip and installs it (not a simple file copy)
