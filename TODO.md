# TODO

Open work on Scripting Nodes v4, roughly in priority order. Keep entries short
and remove them when done (git history has what was done).

## 0. Next, in this order

**1. UX pass.** Go through the add-on as a new user would and collect what's
confusing or slow: node editor (adding, picking, errors on nodes), sidebar
panels (Addon, Addon Data, Group, MCP), first-run experience. Write the
findings here as entries, then fix them.
- [ ] Review and list the findings.
- [ ] Operator and Preferences properties are hard to find: they're edited in the node editor sidebar's Node tab (`draw_buttons_ext`, `nodes/_property_list.py`) while the node is selected, and the node only says "Properties: sidebar (N)" until there is one. The add-on's own properties are in Addon Data. Options: an edit button on the node opening a popup with the list, or showing the selected node's list in Addon Data › Properties too.

**2. Docs: a big pass** (`website/content/docs/`), after the UX pass so the
docs show the final UI.
- [ ] Unwritten pages: Export, Panels, Running Operators, Viewport Drawing.
- [ ] Pages written for older behavior: Buttons (no "Run" label), generated code layout (`utils.py`, no `addon/` package), Trigger nodes left out of exports.
- [ ] Structure and getting started: one path from install to a published add-on; check every page against the current nodes.
- [ ] Regenerate all screenshots (`scripts/docs_screenshots.py`); popups (the Blend Data browser) need a capture of their own, Blender's screenshot leaves them out.

## 1. Generated code quality (extensions platform)

- [ ] Renaming an operator's label renames its idname (and breaks keymaps / buttons in other add-ons that call it). Pin idnames once exported, or a separate "Python name" field.
- [ ] `options={'ANIMATABLE'}` and other property defaults written out.
- [ ] Repeated expressions (`context.scene.my_addon` several times in one statement) into a local variable, see hoisting under 4.
- [ ] Variables as module globals with a compiler-inserted `global` instead of getter / setter pairs (decide).
- [ ] A function parameter named after a builtin (`object`) shadows it.
- [ ] Export check: unescaped data paths (`path_resolve` / msgbus strings built from names); show the issues on the nodes too.

## 2. Properties

- [ ] The Python name follows the label until it's pinned, so renaming a property in use loses saved values. Pin automatically once the add-on was exported?
- [ ] Enum flag properties (sets) have no matching socket type (Data); Set Property needs a set value.
- [ ] Integer limits are edited as floats in the settings.
- [ ] Preferences node: its properties aren't outputs in the Draw flow yet (operators have them).
- [ ] Get / Set for Object properties default to `context.object`, which can be None; no warning.

## 3. Node groups (functions)

- [ ] Pure functions with several outputs are called once per used output (`f(x)[0]`, `f(x)[1]`); value nodes are re-evaluated per use. Decide on hoisting into a variable.
- [ ] Several flow outputs as branches ("Found" / "Not Found"), returned as an index the caller branches on.
- [ ] Interface panels (`new_panel`) are flattened on the Group node.
- [ ] Flow sockets all show one color in the interface list (one socket class).
- [ ] Make Group / Ungroup overwrite the node clipboard.
- [ ] Recursion is blocked (a function can't call itself); decide if recursive functions are wanted.
- [ ] The header picker shows the root tree while editing a group (Blender behavior); the Functions list could open the function in place (path) instead of switching the tree.
- [ ] Function library: groups shared across files (v3 snippets). Link / Append works; asset browser drag & drop doesn't for custom trees. See 9.

## 4. Testing in CI

- [ ] GUI tests (`scripts/test.py --gui`) under `xvfb` in CI.
- [ ] Cache the Blender download; upload the generated add-on and screenshots as artifacts on failure.
- [ ] Functions: Tab and the Add › Groups menu in a GUI test (Make Group / Ungroup and Ctrl+Tab are covered by `tests/gui/groups.py`); save and reopen a file with functions called across trees.
- [ ] Add-on lifecycle:
  - [ ] Persisted add-on stays loaded after opening another file, non-persisted one unloads, persisted add-ons are re-enabled after a Blender restart.
  - [ ] Rename the add-on, restart: the folder of the old name is removed.
  - [ ] Removing or renaming a tree removes its module; `utils.py` disappears when no node uses a helper.
  - [ ] A generated folder without the marker but with the legacy signature is taken over; a user's own add-on with the same name never is.
  - [ ] The `enabled` toggle unloads / reloads; disabling and re-enabling Scripting Nodes while a generated add-on is loaded leaves no stale classes, timers, handlers.
  - [ ] Changing module name / class prefix / idname namespace reloads cleanly.
  - [ ] Two .blend files with the same add-on name; "Save As" copies (shared uid).
  - [ ] The exported zip installs into a clean Blender, enables and disables without errors and without Scripting Nodes installed.
  - [ ] Upgrading Scripting Nodes between versions with a generated add-on on disk.

## 5. Building and releasing

- [ ] Changelog entries in the release notes (now generated from commits).
- [ ] Submit to extensions.blender.org (open: Allow Running Python is on by default; the MCP server is local only, no `online_access` check).
- [ ] `scripts/dev.py` / `build.py` cleanup (the dev loop could symlink the source like the tests instead of rebuilding a zip).
- [ ] Website deploy as part of the release.

## 6. MCP server

- [ ] The first screenshot after Blender starts can show the window before the agent's changes.
- [ ] Moving interface items; panels in interfaces.
- [ ] MCP resources / prompts (the node catalog as a resource, a "build an add-on" prompt).

## 7. Log overlay

- [ ] Show load and runtime errors (core/errors) with a "go to node" action; clear entries per rebuild.
- [ ] Settings (font size, on / off) per user preference instead of per scene.

## 8. Missing nodes

- [ ] **Assets** (v3 had them, asked for again 2026-10-18): files and folders shipped with the add-on (a .blend with node groups / materials, images, presets), listed in **Addon Data › Assets** like Scripts, picked by id. An **Asset** node outputs the path to the shipped copy: `os.path.join(os.path.dirname(__file__), "assets", name)`, copied in with `ctx.asset()` (folders too). Then maybe nodes that use the path directly: append / link from the .blend, load an image. Check with the extensions platform rules (files inside the add-on folder, no writes there).
- [ ] UI List: custom sort function, `panel_prop` per item.
- [ ] Operators: dynamic description (needs property values outside a flow).
- [ ] Reset Variable; full custom property get / set (own storage).
- [ ] Skipped for now: tools, asset shelves, CLI commands, gizmos.

## 9. Extensions

v3 had "Node Extensions": **packages** (zips of extra node files) and
**snippets** (shared node setups). Nothing like it in v4 yet.

- [ ] Decide what an extension is in v4: node packages (third-party node classes against the `ScriptingBaseNode` / `emit(ctx)` API), shared functions (asset libraries, copy / paste as text), or both.
- [ ] Packages: install / remove / list, stored outside the add-on folder, loaded by `auto_load`, errors shown per package. The node API becomes public: needs versioning and docs (`writing-nodes.mdx` is the start).
- [ ] Generated add-ons using package nodes: the package's helpers must end up in the export, or the node is refused on export.

## 10. Smaller things

- [ ] Add-on settings live on `scene.sna`: multi-scene files have one add-on per scene. Decide whether settings move to the window manager / a file-level ID.
- [ ] "Save As" copies keep the add-on uid; renaming the copy removes the original's generated folder.
- [ ] Per-tree compile caching if large files get slow (~40 ms for 300 nodes now).
