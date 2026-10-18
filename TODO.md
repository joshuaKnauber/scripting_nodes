# TODO

Open work on Serpens v4, roughly in priority order. Details and decisions live
in the linked docs/threads; keep entries short and remove them when done.

## 0. Next, in this order

**1. Blend Data browser** (2026-10): a popup from the node's path field
(`blend_data/browser.py`, columns of the path with live values, search in the
live data then all paths; Use Path sets the node's path). Replaced the sidebar
explorer. Open:
- [x] The node shows its path as a button opening the browser (no search field, no start dropdown); the Start column has the node's Data Input.
- [ ] After typing in the search, the first click on a result only ends text editing.
- [ ] Values in the columns are from when the browser moved, not live.
- [ ] Search results found through the types pick collection items by index 0.
- [x] Blender's functions: the Blender Function node (`nodes/categories/data/blender_data/node_blender_function.py`), functions listed in the browser for it, parameters and results as typed sockets. Dragging entries and recent places dropped (popups can't drag into the editor; the browser opens at the node's path).
- [ ] Docs screenshot: Blender's screenshot leaves popups out.

**2. UX pass.** Go through the add-on as a new user would and collect what's
confusing or slow: node editor (adding, picking, errors on nodes), sidebar
panels (Addon, Properties, Group, MCP), first-run experience. Write the
findings here as entries, then fix them.
- [ ] Review and list the findings.

**3. Docs: a big pass** (`website/content/docs/`, 41 pages), after 1 and 2 so
the docs show the final UI.
- [ ] Unwritten pages: Export, Panels, Running Operators, Script Nodes.
- [ ] Pages written for older behavior: Script node (function dropdown, inline code, Data Only), Buttons (no "Run" label), generated code layout (`utils.py`, no `addon/` package), Trigger nodes left out of exports, Blend Data / explorer after the redesign.
- [ ] Structure and getting started: one path from install to a published add-on; check every page against the current nodes.
- [ ] Regenerate all screenshots (`scripts/docs_screenshots.py`) once the UI is final.

## 1. Generated code quality (extensions platform)

Serpens add-ons get rejected on extensions.blender.org for messy code. Goal: an
exported add-on reads like hand-written code and passes the
[moderation guidelines](https://developer.blender.org/docs/features/extensions/moderation/guidelines/)
and `ruff check` with zero findings.

- [x] **Readable names** (2026-10): modules, classes, operator idnames and functions come from labels (`main.py`, `MESH_HELPER_OT_duplicate`, `mesh_helper.duplicate`, `greet`), suffix only on collision, claimed in one pass in a fixed order (`core/naming.py`, nodes declare `sn_names()`). Locals `row`, `row_2`.
  - [x] Property names come from the property lists (unique per list, optional pinned Python name).
  - [ ] Renaming an operator's label renames its idname (and breaks keymaps / buttons in other add-ons that call it). Consider pinning idnames once exported, or a separate "Python name" field.
- [x] **Baseline** (2026-10): example add-on Object Toolkit (`tests/visual/scenarios/_toolkit_demo.py`, `scripts/example_addon.py`), export snapshot in `tests/snapshots/object_toolkit/`, zero findings with `tests/snapshots/ruff.toml` and `ruff format`-clean, checked in CI.
- [x] **No default arguments** (2026-10): `ctx.keyword()` / `ctx.args()` leave out Blender's defaults; no `poll()` returning `True`, empty `bl_description`, `bl_order = 0`, `bl_options = set()`, `execute()` of modal operators, UIList `bl_idname`. Buttons without a label show the operator's name (Icon Only for none).
  - [ ] `options={'ANIMATABLE'}` and other property defaults.
- [x] **Conventional layout** (2026-10): `__init__.py` imports the modules and registers an explicit `classes` tuple in dependency order (`core/package.py`); no `auto_load.py`, `sys.modules` alias, `addon/` subpackage, empty `register()` or unused `import bpy`; `bl_info` only in the live add-on. Imports sorted like isort; properties.py imports update callbacks at the top when there's no cycle.
  - [x] Helpers in `utils.py`, called as `utils.report(...)` (no `sn_` prefixes); Trigger nodes are left out of exports, empty tree modules aren't written.
- [x] **Export clean-up pass** (2026-10): autopep8 (and the bundled wheels) replaced by `lib/python_format.py`, which formats like `ruff format`; redundant parentheses removed (AST-checked); f-strings from Format String; `x.name = ...` instead of `setattr` with a constant; no `float()` around integers; no conversions of values already of the type.
  - [ ] Repeated expressions (`context.scene.my_addon` several times in one statement) into a local variable - see the hoisting question in 4.
- [ ] **`context` over `bpy.context`**: `ctx.context` exists (`context` inside functions that have it, else `bpy.context`) and property nodes use it; move the Scene node and friends to it.
- [ ] **Node polish**: For Each without unused index, Print takes any value (no `str()`), variables as module globals with compiler-inserted `global` (instead of getter/setter pairs - decide).
- [x] **Trigger nodes are dev only** (2026-10): left out of export builds (`sn_dev_only`).
- [x] **Function signatures** (2026-10): functions only declare (and calls only pass) what the body uses from the caller (`def header(*, layout)`); functions compile before their callers.
  - [ ] A parameter named after a builtin (`object`) shadows it.
- [x] **Export check** (2026-10): `core/export_check.py`, sidebar Addon › Extensions Platform (also run on export): `bpy.data` collections, data-blocks by name, writing into the add-on folder, `sys` changes, `__name__` / `bl_ext`, files / network / clipboard without the permission, network without `online_access`, keyconfig without a None check, missing author / tagline. Issues inside a value node's expression are blamed on that node.
  - [ ] Unescaped data paths (`path_resolve` / msgbus strings built from names); show the issues on the nodes too.
- [x] **Regression test** (2026-10): the Object Toolkit snapshot, plus an add-on with every node (`tests/visual/scenarios/_every_node_demo.py`, `scripts/example_addon.py every_node`) checked with ruff in CI (constant conditions from unconnected inputs ignored).

## 2. Add-on metadata

- [x] Fields on the addon settings: version, maintainer/author, tagline, description, website, tags, license, minimum Blender version. Written to `blender_manifest.toml` (and the GPL header), no `"Unknown"` placeholders.
- [ ] Permissions derived from the nodes used (`files`, `network`, `clipboard`, ...) with a reason text the user can edit.
- [x] Problems shown in the sidebar; `extension validate` runs in the tests.
- [x] Icons bundled with the add-on (`icons/`).

## 3. Node design open questions

- [x] **Blend Data** (done 2026-10, `website/content/docs/blend-data/`): one Blender Data node following a path (Context / Blend File / Input), add-menu presets, typed sockets from RNA with a type picker for open types, `[]` keys by Index / Name / Active, paste + "Copy Data Path for Scripting Nodes", property nodes in Blender mode use the same paths. Follow-ups:
  - [x] Data explorer v1 (sidebar Blend Data tab), replaced by the path browser popup (see 0).
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

- [x] `.github/workflows/ci.yml`: Blender 5.0 + 5.1 on Linux, ruff (repo and generated example add-on), `extension validate`, headless suite.
- [ ] GUI tests (`scripts/test.py --gui`) under `xvfb` in CI.
- [ ] Cache the Blender download; upload the generated fixture add-on and screenshots as artifacts on failure.
- [ ] Code-quality job for generated add-ons (see 1).
- [ ] Functions: Tab / Ctrl+Tab and the Add > Groups menu in a GUI test (Make Group / Ungroup are covered by `tests/gui/groups.py`); save and reopen a file with functions called across trees.
- [ ] **Add-on lifecycle coverage.** Already tested: hot reload, rollback on syntax/import errors, rename removes the old add-on, foreign folders untouched, deleting all trees unloads, save → open other → reopen, real undo/redo (GUI), export build. Missing:
  - [ ] *Persist* across file switches: persisted add-on stays loaded after opening another file, non-persisted one unloads, persisted add-ons are re-enabled after a Blender restart (`generated_addons.json` in the extension user dir).
  - [ ] Rename across sessions: rename the add-on, restart, the folder of the old name is removed (persistence `module_for`).
  - [ ] Stale files: removing or renaming a tree removes its module; `utils.py` disappears when no node uses a helper.
  - [ ] Folders from older versions: a generated folder without the marker but with the legacy signature is taken over; a user's own add-on with the same name never is.
  - [ ] Disabling: the addon `enabled` toggle unloads/reloads; disabling and re-enabling Serpens while a generated add-on is loaded (no stale classes, timers, handlers).
  - [ ] Module name / class prefix / idname namespace overrides: changing them reloads cleanly under the new names.
  - [ ] Two .blend files with the same add-on name; "Save As" copies (shared uid).
  - [ ] Export: the zip installs into a clean Blender (`extension install-file`), enables, registers and unregisters without errors and without Serpens installed.
  - [ ] Upgrading Serpens itself between versions with a generated add-on on disk.

## 6. Building and releasing

- [x] One version source (manifest); CI releases `v<version>` when it changes on main (pre-release with a suffix like `-beta.1`), "Run workflow" releases by hand.
- [ ] Changelog entries in the release notes (now generated from commits).
- [x] Scripting Nodes passes its own export check (2026-10): clipboard permission, no `bl_ext` parsing, no `sys` changes (runtime errors via wrapping, reloads via `lib/reloading.py`), no import-time `driver_namespace` write.
- [ ] Submit to extensions.blender.org (open: Allow Running Python is on by default; the MCP server is local only, no `online_access` check).
- [ ] `scripts/dev.py` / `build.py` cleanup (dev loop could symlink the source like the tests instead of rebuilding a zip).
- [ ] Website deploy as part of the release; docs screenshots regenerated (`scripts/docs_screenshots.py`).

## 7. MCP server

Done (2026-10): 24 tools in `mcp_server/tools/` (Blender: run_python, screenshot, undo, logs; add-on: settings, problems incl. the export check, code, export, run_operator; graph: batched edit_tree with sockets by key and refs, properties, functions, texts, data path search, show_tree). One undo step per call, tool errors say what to do, failed edit_tree batches remove their nodes, timed-out calls don't run late, optional token, Allow Running Python, Start with Blender. Tested: every tool area (`tests/test_mcp_tools.py`), the Object Toolkit built only through the tools matches the snapshot, HTTP + screenshots + undo in a real window (`tests/gui/mcp.py`). Docs: `ai/mcp-server.mdx`, `ai/agents.mdx`.

- [ ] The first screenshot after Blender starts can show the window before the agent's changes (later ones are current).
- [x] make_group / ungroup (the Ctrl G operators, in a node editor: an area is borrowed if none is open).
- [ ] Moving interface items; panels in interfaces.
- [ ] MCP resources / prompts (e.g. the node catalog as a resource, a "build an add-on" prompt).
- [x] `blender_version_min` defaults to the Blender the add-on is made in.

## 8. Log overlay

- [x] Move the import-time `driver_namespace` write into `register()`; the overlay is fed by `lib.logger` listeners and the `sn_print` helper.
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
- [x] UI List (`template_list`; Blender's own name filter / sort). Not done: custom filter / sort functions, `panel_prop` per item.
- [x] Operators: File Browser invoke type (open file(s), save, folder, filter), dialog title / message / confirm text / width, Depends on Cursor, Return node. Not done: dynamic description (needs property values outside a flow).
- [x] File Handler (drag and drop import; generated auto_load registers FileHandler / AssetShelf classes).
- [x] Modal operators: Start / Modal / End flows, Event, timer, Esc cancel; Return, Is Key, Set Header / Status Text, Set Cursor (`tests/gui/operators.py`).

- [ ] **Migrating v3 files** (maybe): a one-time import of a v3 .blend into v4 trees. Map what has an equivalent, leave a note node for the rest, report what wasn't converted.

## 10. Smaller things

- [ ] Addon settings live on `scene.sna`: multi-scene files have one addon per scene. Decide whether settings move to the window manager / a file-level ID.
- [ ] "Save As" copies keep the addon uid; renaming the copy removes the original's generated folder (persistence).
- [ ] Per-tree compile caching if large files get slow (currently ~40 ms for 300 nodes).
- [ ] `normalize_indents` in `lib/code_format.py` is unused now.

## 11. Extensions

v3 had "Node Extensions" (sidebar panel): **packages**, zips of extra node files extracted into the add-on's `nodes/` folder, and **snippets**, shared node setups. Nothing like it in v4 yet.

- [ ] Decide what an extension is in v4: node packages (third-party node classes against the `ScriptingBaseNode` / `emit(ctx)` API), shared functions (see the function library under 4), or both.
- [ ] Packages: install / remove / list, stored outside the add-on folder (updating Scripting Nodes mustn't delete them), loaded by `auto_load`, errors shown per package. The node API they build on becomes public: needs versioning and docs (`writing-nodes.mdx` is the start).
- [ ] Generated add-ons that use package nodes: the package's helpers must end up in the export, or the node is refused on export.
