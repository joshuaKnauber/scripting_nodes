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

- [x] Fields on the addon settings: version, maintainer/author, tagline, description, website, tags, license, minimum Blender version. Written to `blender_manifest.toml` (and the GPL header), no `"Unknown"` placeholders.
- [ ] Permissions derived from the nodes used (`files`, `network`, `clipboard`, ...) with a reason text the user can edit.
- [x] Problems shown in the sidebar; `extension validate` runs in the tests.
- [x] Icons bundled with the add-on (`icons/`).

## 3. Node design open questions

- [x] **Blend Data** (done 2026-10, `website/content/docs/blend-data/`): one Blender Data node following a path (Context / Blend File / Input), add-menu presets, typed sockets from RNA with a type picker for open types, `[]` keys by Index / Name / Active, paste + "Copy Data Path for Scripting Nodes", property nodes in Blender mode use the same paths. Follow-ups:
  - [x] Data explorer v1 (sidebar Blend Data tab): a browser of live data, one level at a time, path shown as code, + adds nodes, editable values, Go to Its Path / Use This Path for the selected node, types-only fallback.
  - [ ] Explorer: Blender's functions (`objects.new()`, `modifiers.remove()`), needs a node that calls them.
  - [ ] Explorer: drag entries into the node editor; remember recent places.
- [x] **Node references** (done 2026-10): `Reference(...)` fields with a search callback, stored by node id, "Used by" in the sidebar, copies point at copied targets, deleted targets drawn red.
- [x] **Properties as lists** (done 2026-10, `website/content/docs/properties/properties.mdx`): add-on list in Addon Data (one PropertyGroup per attach type, `scene.my_addon.count`), groups with their own list, Operator / Preferences node lists (operator properties are also its outputs), Get / Set / fields / On Property Update pick by id, enum items and pointer poll from functions, `addon/properties.py`. Follow-ups:
  - [ ] The Python name follows the label until it's pinned, so renaming a property in use loses saved values. Pin automatically once the add-on was exported?
  - [ ] Enum flag properties (sets) have no matching socket type (Data); Enum Menu / Get Property work, Set Property needs a set value.
  - [ ] Integer limits are edited as floats in the settings.
  - [ ] Preferences node: its properties aren't outputs in the Draw flow yet (operators have them).
  - [ ] Get/Set for Object properties default to `context.object`, which can be None; no warning.
  - [ ] Displaying collections (UI list node) - see v3 parity.

## 4. Node groups (functions)

Done (2026-10): native groups - the tree interface (sidebar Group tab) + Blender's Group Input / Output, our Group node, Ctrl+G / Ctrl+Alt+G / Tab, Add > Groups, docs with screenshots (`website/content/docs/nodes/functions/`), demo scenario `tests/visual/scenarios/_functions_demo.py`. Verified by hand in a real file.

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

## 9. Missing nodes (v3 parity + Blender API)

Agreed 2026-10-14, in this order. Viewport drawing, tools, asset shelves, CLI commands and gizmos are skipped for now.

**1. Small, needed by everyone (and empty docs pages)**
- [x] Add to Menu / Panel / Header: append or prepend to Blender's own classes (Python-defined ones; C panels like the sidebar's Transform can't be extended). A click-to-pick location (like the Panel node's) could follow.
- [x] Timers: Run with Delay, Run in Intervals (`bpy.app.timers`, stopped when the add-on is disabled).
- [x] Shortcuts: keymap entries running an operator or opening a menu (addon keyconfig, `tests/gui/shortcuts.py`). Pie menus once they exist.
- [x] Report (info / warning / error from an operator, printed elsewhere).
- [x] String nodes: Split, Join List, Replace, Trim, Pad, Length, Slice, Change Case, Find, Format, Starts / Ends With (Substring In String). Encode / Decode skipped (bytes don't fit any socket).

**2.**
- [x] Get / Set Custom Property (set or remove; `Exists` output).
- [x] Get / Set Attribute by name.
- [x] Python Expression / Python Statement: unknown names become inputs, modules auto-imported.
- [x] File nodes (read / write text, create folder, list folder, join path, path info, load from / list .blend). Nodes declare `sn_permissions`; the manifest and sidebar pick them up. Other permissions (network, clipboard) once nodes need them.
- [x] Pie Menu, Popover, Open Menu (menus, pies, panels); Shortcut opens all three. Menu classes exist without a button (`emit_module`).
- [x] Combine / Separate Vector, Convert Angle, Random Value, Current Time, Is in Mode, Is Object Type, Area by Type, Add-on Info, Set Variable Change By / Toggle, Icon from Data, Repeat, Break / Continue, Switch (instead of Enum Map), Redraw. Not done: Reset Variable (set it to its value), Edit Select Mode (Blender Data: `tool_settings.mesh_select_mode`).

**3.**
- [x] On Blender Change (`bpy.msgbus`, by type; re-subscribed after loading a file; `tests/gui/layouts.py`).
- [x] Handlers: render init / cancel / write, playback, append / link, load / save fail, bake, composite. Skipped: render_stats, factory startup, translation, xr.
- [x] Text Field (text box, search, placeholder), Enum Menu (icon view), Pointer Field (template_ID), Operator Menu, Set Context Data, operator context on Set Layout State, Split, Grid, Draw For Each, Progress, Menu Contents. Dropped: prop_tabs_enum (draws garbled in panels), props_enum / prop_enum (Enum Menu Expand covers them).
- [x] Properties: integer / boolean vectors, string Search Function, Get / Set Functions (`get_transform` / `set_transform`), attach types Bone, PoseBone, Node, Strip, ViewLayer, WorkSpace, Curve, GreasePencil, Brush, Action, Texture. Not done: full custom get / set (own storage).

**4.**
- [ ] UI List (`template_list`, filter / sort) with `panel_prop` per item.
- [ ] Operators: file browser (`fileselect_add`, filter), custom dialog layout + title / confirm text / width, dynamic description, depends on cursor.
- [ ] File Handler (drag and drop import).
- [ ] Modal operators: modal flow, event, return state, cursor, header / status text.

- [ ] **Migrating v3 files** (maybe): a one-time import of a v3 .blend into v4 trees. Map what has an equivalent, leave a note node for the rest, report what wasn't converted.

## 10. Smaller things

- [ ] Addon settings live on `scene.sna`: multi-scene files have one addon per scene. Decide whether settings move to the window manager / a file-level ID.
- [ ] "Save As" copies keep the addon uid; renaming the copy removes the original's generated folder (persistence).
- [ ] Per-tree compile caching if large files get slow (currently ~40 ms for 300 nodes).
- [ ] `normalize_indents` in `lib/code_format.py` is unused now.
