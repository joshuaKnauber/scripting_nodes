# TODO

Open work on Serpens v4, roughly in priority order. Details and decisions live
in the linked docs/threads; keep entries short and remove them when done.

## 1. Generated code quality (extensions platform)

Serpens add-ons get rejected on extensions.blender.org for messy code. Goal: an
exported add-on reads like hand-written code and passes the
[moderation guidelines](https://developer.blender.org/docs/features/extensions/moderation/guidelines/)
and `ruff check` with zero findings.

- [x] **Readable names** (2026-10): modules, classes, operator idnames and functions come from labels (`main.py`, `MESH_HELPER_OT_duplicate`, `mesh_helper.duplicate`, `greet`), suffix only on collision, claimed in one pass in a fixed order (`core/naming.py`, nodes declare `sn_names()`). Locals `row`, `row_2`.
  - [x] Property names come from the property lists (unique per list, optional pinned Python name).
  - [ ] Renaming an operator's label renames its idname (and breaks keymaps / buttons in other add-ons that call it). Consider pinning idnames once exported, or a separate "Python name" field.
- [ ] **No default arguments**: `ctx.args(...)` helper drops defaults; skip `poll()` returning `True`, empty `bl_description`, `bl_order = 0`, `options={'ANIMATABLE'}`, ...
- [ ] **Conventional layout**: `__init__.py` imports the tree modules and registers an explicit `classes = (...)` tuple in dependency order. Drop `auto_load.py`, `bl_info`, the `sys.modules` alias (violates "sys is read-only"), the `addon/` subpackage and empty `register()`.
- [ ] **Export clean-up pass**: `ast.unparse` (redundant parens, quotes) + blank lines + unused import removal.
- [ ] **`context` over `bpy.context`**: `ctx.context` exists (`context` inside functions that have it, else `bpy.context`) and property nodes use it; move the Scene node and friends to it.
- [ ] **Node polish**: For Each without unused index, Print takes any value (no `str()`), variables as module globals with compiler-inserted `global` (instead of getter/setter pairs - decide).
- [ ] **Trigger nodes are dev only**: left out of export builds.
- [ ] **Function signatures**: functions always declare `*, self=None, context=None, layout=None, event=None` and `context = context or bpy.context`; only declare and pass what the body uses.
- [ ] **Export check**: before writing the zip, list guideline issues on the nodes (hard-coded data-block names, `bpy.data.objects`, unescaped data paths, missing permissions, unused/undefined names).
- [ ] **Regression test**: export a fixture add-on using every node; require zero ruff findings plus a snapshot of the output.

## 2. Add-on metadata

- [ ] Fields on the addon settings: version, maintainer/author, tagline, description, website, tags, license, minimum Blender version. Written to `blender_manifest.toml` (and the GPL header), no `"Unknown"` placeholders.
- [ ] Permissions derived from the nodes used (`files`, `network`, `clipboard`, ...) with a reason text the user can edit.
- [ ] Validate on export (`blender --command extension validate`) and show problems in the sidebar.
- [ ] Assets/icons bundled with the add-on (v3 had this).

## 3. Node design open questions

- [ ] **Blend Data**: separate design thread ("Design: Blend Data in Serpens v4", worktree `blend-data-v4`). Includes: Blender-path mode doesn't know the property type (Set Property gets a generic Data input).
- [ ] **Node references**: separate design thread ("Design: node references in Serpens v4"). Picker collections on `scene.sna` with hashed names, scene-level storage, linear lookups.
- [x] **Properties as lists** (done 2026-10, `website/content/docs/nodes/properties.mdx`): add-on list in Addon Data (one PropertyGroup per attach type, `scene.my_addon.count`), groups with their own list, Operator / Preferences node lists (operator properties are also its outputs), Get / Set / fields / On Property Update pick by id, enum items and pointer poll from functions, `addon/properties.py`. Follow-ups:
  - [ ] The Python name follows the label until it's pinned, so renaming a property in use loses saved values. Pin automatically once the add-on was exported?
  - [ ] Enum flag properties (sets) have no matching socket type (Data); Enum Menu / Get Property work, Set Property needs a set value.
  - [ ] Integer limits are edited as floats in the settings.
  - [ ] Preferences node: its properties aren't outputs in the Draw flow yet (operators have them).
  - [ ] Get/Set for Object properties default to `context.object`, which can be None; no warning.
  - [ ] Displaying collections (UI list node) - see v3 parity.

## 4. Node groups (functions)

Done (2026-10): native groups - the tree interface (sidebar Group tab) + Blender's Group Input / Output, our Group node, Ctrl+G / Ctrl+Alt+G / Tab, Add > Groups, docs with screenshots (`website/content/docs/nodes/functions.mdx`), demo scenario `tests/visual/scenarios/_functions_demo.py`. Verified by hand in a real file.

- [ ] Pure functions with several outputs are called once per used output (`f(x)[0]`, `f(x)[1]`); value nodes in general are re-evaluated per use (Greet computes its string twice). Decide on hoisting into a variable.
- [ ] Several flow outputs as branches ("Found" / "Not Found"), returned as an index the caller branches on.
- [ ] Interface panels (`new_panel`) are flattened on the Group node.
- [ ] Flow sockets all show one color in the interface list (one socket class); kind is only visible on the nodes.
- [ ] Make Group / Ungroup overwrite the node clipboard.
- [ ] Recursion is blocked (a function can't call itself); decide if recursive functions are wanted.
- [ ] The `ScriptingNodeTree` header picker shows the root tree while editing a group (Blender behavior); the Functions list in the sidebar could open the function in place (path) instead of switching the tree.
- [ ] Function library: groups shared across files (v3 snippets). Link/Append works; asset browser drag & drop doesn't for custom trees (Blender's group asset operators are built-in-tree only).

## 5. Testing in CI

- [ ] Get `.github/workflows/ci.yml` running (it has never run: nothing pushed yet). Blender 5.0 + 5.1 on Linux, ruff, `extension validate`, headless suite.
- [ ] GUI tests (`scripts/test.py --gui`) under `xvfb` in CI.
- [ ] Cache the Blender download; upload the generated fixture add-on and screenshots as artifacts on failure.
- [ ] Code-quality job for generated add-ons (see 1).
- [ ] Functions: Tab / Ctrl+Tab and the Add > Groups menu in a GUI test (Make Group / Ungroup are covered by `tests/gui/groups.py`); save and reopen a file with functions called across trees.
- [ ] **Add-on lifecycle coverage.** Already tested: hot reload, rollback on syntax/import errors, rename removes the old add-on, foreign folders untouched, deleting all trees unloads, save → open other → reopen, real undo/redo (GUI), export build. Missing:
  - [ ] *Persist* across file switches: persisted add-on stays loaded after opening another file, non-persisted one unloads, persisted add-ons are re-enabled after a Blender restart (`generated_addons.json` in the extension user dir).
  - [ ] Rename across sessions: rename the add-on, restart, the folder of the old name is removed (persistence `module_for`).
  - [ ] Stale files: removing or renaming a tree removes its module; `_sn_helpers.py` disappears when no node uses a helper.
  - [ ] Folders from older versions: a generated folder without the marker but with the legacy signature is taken over; a user's own add-on with the same name never is.
  - [ ] Disabling: the addon `enabled` toggle unloads/reloads; disabling and re-enabling Serpens while a generated add-on is loaded (no stale classes, timers, handlers, excepthook).
  - [ ] Module name / class prefix / idname namespace overrides: changing them reloads cleanly under the new names.
  - [ ] Two .blend files with the same add-on name; "Save As" copies (shared uid).
  - [ ] Export: the zip installs into a clean Blender (`extension install-file`), enables, registers and unregisters without errors and without Serpens installed.
  - [ ] Upgrading Serpens itself between versions with a generated add-on on disk.

## 6. Building and releasing

- [ ] One version source (manifest) and a release script: bump version, changelog entry, `blender --command extension build`, tag.
- [ ] GitHub release with the zip; decide on extensions.blender.org submission for Serpens itself (it must pass the same guidelines: e.g. `log_overlay.py` writes to `bpy.app.driver_namespace` at import time, MCP server needs the `network` permission and an `online_access` check if it ever goes beyond localhost).
- [ ] `scripts/dev.py` / `build.py` cleanup (dev loop could symlink the source like the tests instead of rebuilding a zip).
- [ ] Website deploy as part of the release; docs screenshots regenerated (`scripts/docs_screenshots.py`).

## 7. MCP server

- [ ] Update the tools to the new node API: socket keys instead of indices/names, flow socket `kind`, references by id, node code from the last build (`compiler.node_lines`), `mark_dirty()`.
- [ ] Tools for property lists (add / edit / pick properties).
- [ ] Tools for functions: create a function, add/rename/move interface items (`tree.interface`), set a Group node's `node_tree`, make group from nodes. `is_group` is now `is_function` in the tree tools.
- [ ] Tests for the tools (create nodes, link, set properties, read code) - currently only the security checks are tested.
- [ ] Optional bearer token, a timeout that doesn't run queued calls after the client gave up, split `tools.py` (1400 lines) into read/write modules.
- [ ] Docs page for using it with Claude Code / Codex.

## 8. Log overlay

- [ ] Move the import-time `driver_namespace` write into `register()`; the overlay is fed by `lib.logger` listeners and the `sn_print` helper.
- [ ] Show load and runtime errors (core/errors) with a "go to node" action; clear entries per rebuild.
- [ ] Settings (font size, on/off) per user preference instead of per scene.

## 9. v3 parity (after the code quality work)

Add To Panel / Menu, modal operators, timers (run with delay / intervals), keymaps/shortcuts, Report, loops (repeat, break), UI lists, popovers/pie menus, inline Python line, file and string utility nodes. See the v3 comparison in the session notes.

- [ ] **Migrating v3 files** (maybe): a one-time import of a v3 .blend into v4 trees. v4 doesn't have to load v3 files, but users have years of graphs. Map what has an equivalent (operators, panels, properties, layouts, run operator, ...), leave a note node for the rest, report what wasn't converted. Decide after the property design and parity work, since both define what v3 maps onto. Could start with properties and the sidebar data (simplest, most reused).

## 10. Smaller things

- [ ] Addon settings live on `scene.sna`: multi-scene files have one addon per scene. Decide whether settings move to the window manager / a file-level ID.
- [ ] "Save As" copies keep the addon uid; renaming the copy removes the original's generated folder (persistence).
- [ ] Per-tree compile caching if large files get slow (currently ~40 ms for 300 nodes).
- [ ] `normalize_indents` in `lib/code_format.py` is unused now.
