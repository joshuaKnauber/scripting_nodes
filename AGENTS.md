# Scripting Nodes - Agent Handbook

## 1. Project Snapshot
- Visual scripting add-on targeting Blender 4.3; ships under `addon/scripting_nodes` with `__init__.py` registering via `auto_load.py`.
- Goal: let users construct Blender add-ons through node graphs that generate Python modules.
- Runtime state is stored on `bpy.context.scene.sna` (see `addon/scripting_nodes/src/features/settings`), which controls dev flags and generated addon metadata.

## 2. Repository Layout
- `addon/`: Blender add-on package copied into Blender's add-ons directory.
  - `scripting_nodes/auto_load.py`: discovers submodules, topologically registers classes.
  - `scripting_nodes/src/`: core source tree (features, handlers, libraries, utils).
    - `features/nodes/`: node definitions grouped by category; every node subclasses `features/nodes/base_node.py`.
    - `features/node_tree/`: custom `ScriptingNodeTree`, code generation pipeline, operators, UI integration.
    - `features/settings/`: `Scene.sna` property groups (addon/dev/ui settings, node references).
    - `features/sockets/`: custom socket classes and utilities.
    - `handlers/`: Blender handlers for events, msgbus, timers; `timers/node_tree_watcher.py` hooks the code-gen watcher.
    - `lib/`: shared utilities (code formatting, logging, bpy helpers, name generator, autopep8 vendor drop-in).
    - `assets/`: placeholder for bundled resources (currently empty).
- `scripts/`: host tooling.
  - `dev.py`: syncs the local addon into Blender's add-ons directory, launches Blender, handles restart shortcuts.
  - `build.py`: packages the addon into `builds/scripting_nodes_<version>.zip`.
- `config.template.yaml`: sample config; copy to `config.yaml` with machine-specific Blender paths (ignored by Git).
- `requirements.txt`: Python tooling needed for scripts (`fake-bpy-module`, `pyyaml`, `psutil`, `colorama`).
- `venv/`: committed convenience virtualenv. Prefer local venvs for isolation; avoid modifying this copy.

## 3. Environment and Tooling Setup
1. Use Python 3.12+ (matches Blender 4.3 bundle). Recommended: create a fresh virtualenv outside `venv/`.
2. `python -m venv .venv` and activate (`.\.venv\Scripts\activate` on Windows).
3. `pip install -r requirements.txt`.
4. Duplicate `config.template.yaml` -> `config.yaml` and set:
   - `BLENDER_EXECUTABLE`: path to Blender executable to launch for the dev loop.
   - `ADDONS_PATH`: Blender user add-ons directory (where dev sync copies files).
5. Keep `config.yaml` out of version control (already ignored).

## 4. Development Workflow
- Run `python .\scripts\dev.py` from repo root. The script will:
  1. Sync `addon/scripting_nodes` into `<ADDONS_PATH>/scripting_nodes`.
  2. Launch Blender with `--python-use-system-env` so it can see your virtualenv packages.
  3. Stream stdout/stderr with colored prefixes.
  4. Accept hotkeys in the console: press `r` to resync and relaunch after code edits, `q` to stop.
- Dev script auto-terminates any running Blender matching `BLENDER_EXECUTABLE` before relaunching.
- Blender side (`handlers/timers/node_tree_watcher.py`) keeps the generated addon module up to date by watching `scene.sna` dirtiness flags.
- Typical edit loop:
  1. Modify Python under `addon/scripting_nodes/src`.
  2. Inside Blender, trigger rebuild (nodes mark themselves dirty automatically). If structural Python changes require reload, press `r` in the dev console.
  3. Inspect `Scene > Scripting Nodes` properties for dev toggles such as `Show Node Code` or `Log Tree Rebuilds`.

## 5. Build and Release
- Run `python .\scripts\build.py` and provide a semantic version (for example `4.0.1`).
- Script creates `builds/scripting_nodes_<version>.zip` ready for distribution; intermediate folder is cleaned after zipping.
- Ensure production assets are regenerated first: in Blender enable "Force Production" or toggle `scene.sna.addon.force_production` before exporting if needed.

## 6. Key Runtime Concepts
- **Auto-registration**: `auto_load.py` recursively imports every submodule and orders class registration via dependency analysis (ensures panels/operators register after their dependencies).
- **Node trees**: `ScriptingNodeTree` (`src/features/node_tree/node_tree.py`) handles link tracking, group socket synchronization, reroute upkeep, and reference management. Nodes set `is_dirty` to flag regeneration.
- **Code generation**: `src/features/node_tree/code_gen/generator.py` rebuilds Python modules for each node tree into either a dev module (`scripting_nodes_temp`) or production package. `watcher.py` triggers regeneration and hot reload.
- **Scene store**: `Scene.sna` aggregate holds addon settings (`addon_properties.py`), developer options (`dev_properties.py`), UI state, and a reference collection linking generated code to nodes.
- **Sockets and references**: custom sockets live under `src/features/sockets`; utilities help with dynamic sockets and link traversal (`lib/utils/sockets`).
- **Handlers**: event handlers respond to file load/save, depsgraph updates, etc., ensuring modules persist across sessions and watchers stay registered.

## 7. Coding Standards and Patterns
- Follow Blender API expectations (subclass `bpy.types.Node`, `Operator`, etc.) and register via `auto_load`.
- Keep Python roughly PEP 8; repository vendors `autopep8.py` for formatting support if desired, but external formatting is not automated.
- Nodes should:
  - Subclass `ScriptingBaseNode` (see `features/nodes/base_node.py`).
  - Define `bl_idname`, `bl_label`, sockets in `on_create`, and implement `generate()` to populate output code strings.
  - Use `sn_options` to mark root nodes (`{"ROOT_NODE"}`) that trigger tree rebuilds.
  - Manage dynamic sockets via provided helpers (`add_input`, `add_output`).
- Code interacting with generated files must honour dirtiness flags (`is_dirty`, `node_tree.is_dirty`) to avoid unnecessary rebuilds.
- When introducing new handlers or property groups, ensure they cleanly register/unregister to avoid Blender residual state.
- External dependencies should be added to `requirements.txt` and, if needed in Blender runtime, bundled or lazily imported.

## 8. Testing and Validation
- No automated tests are present; validation is manual within Blender.
- Recommended checklist before handing off changes:
  - Launch the dev loop (`scripts/dev.py`) and confirm the addon loads with no console errors.
  - Create sample node trees to ensure new nodes/operators behave and generated modules execute via `scene.sna.execute`.
  - Watch console output (`Log Tree Rebuilds`) to ensure dirtiness propagation functions as expected.
  - For release builds, test installing the produced zip in a clean Blender profile.

## 9. Helpful Commands and Paths
- `python .\scripts\dev.py`: sync and launch Blender dev session.
- `python .\scripts\build.py`: produce distributable zip.
- `rg <pattern> addon/scripting_nodes/src`: fast code search.
- Generated dev addon path: `<ADDONS_PATH>\scripting_nodes` (overwritten on each sync).
- Temporary dev module inside Blender: `scripting_nodes_temp` (see `lib/constants/paths.py`).

## 10. Tips for Future Agents
- Use Context7 (`resolve-library-id` then `get-library-docs`) to check the most current Blender Python API (`bpy`) documentation when available. This ensures you're referencing up-to-date API signatures and best practices.
- Never edit files inside Blender's add-ons directory directly; treat `addon/` as the source of truth and let tooling copy it.
- Respect user-specific configs: avoid committing `config.yaml` or machine-specific paths.
- Large directories (`addon/scripting_nodes/src/features/nodes/categories/*`) house many node definitions; add new nodes by mirroring existing category patterns and updating registries if necessary.
- If Blender fails to relaunch, verify the dev script terminated previous instances; occasionally a hung process needs a manual kill.
- When adding persistent modules or assets, update the code-gen folders under `src/features/node_tree/code_gen/file_management` so builds include them.
- Keep logs meaningful: use `lib/utils/logger.log_if` for gated console output that honours dev settings.

