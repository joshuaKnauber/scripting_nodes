# TODO

Open work on Serpens v4, roughly in priority order. Details and decisions live
in the linked docs/threads; keep entries short and remove them when done.

## 1. Generated code quality (extensions platform)

Serpens add-ons get rejected on extensions.blender.org for messy code. Goal: an
exported add-on reads like hand-written code and passes the
[moderation guidelines](https://developer.blender.org/docs/features/extensions/moderation/guidelines/)
and `ruff check` with zero findings.

- [ ] **Readable names**: derived from labels instead of ids (`copies`, `MESH_HELPER_OT_duplicate`, `mesh_helper.duplicate`, `main.py`), suffix only on collision, assigned in a fixed order so builds are stable. Locals `row`, `row_2`. Property nodes keep an optional "Python name" to pin a name (renaming would lose saved values).
- [ ] **No default arguments**: `ctx.args(...)` helper drops defaults; skip `poll()` returning `True`, empty `bl_description`, `bl_order = 0`, `options={'ANIMATABLE'}`, ...
- [ ] **Conventional layout**: `__init__.py` imports the tree modules and registers an explicit `classes = (...)` tuple in dependency order. Drop `auto_load.py`, `bl_info`, the `sys.modules` alias (violates "sys is read-only"), the `addon/` subpackage and empty `register()`.
- [ ] **Export clean-up pass**: `ast.unparse` (redundant parens, quotes) + blank lines + unused import removal.
- [ ] **`context` over `bpy.context`**: `ctx.context` resolves to the function's `context` where available (Scene node and friends).
- [ ] **Node polish**: For Each without unused index, Print takes any value (no `str()`), variables as module globals with compiler-inserted `global` (instead of getter/setter pairs - decide).
- [ ] **Trigger nodes are dev only**: left out of export builds.
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
- [ ] Flows can't return a value outside group trees (Pointer Property poll needs a group tree). Decide on a Return node or callable flows.
- [ ] `PropertyNode.property_args(ctx)` runs with the container's ctx and can't read its own inputs.
- [ ] Run Operator / Button: vector/color properties of SN operators always get 3 components, no alpha.

## 4. Node groups

- [ ] Review the UX: creating a group from selected nodes, Tab in/out (keymaps exist), editing parameters (currently a JSON list with add/remove buttons; no reordering, renaming or types after creation).
- [ ] Groups compile to `def group(params, *, self=None, context=None, layout=None, event=None)`; check that interface groups (drawing UI) and data-only calls are covered by tests.
- [ ] Recursion / nested groups, groups shared across files (v3 snippets), a group library.

## 5. Testing in CI

- [ ] Get `.github/workflows/ci.yml` running (it has never run: nothing pushed yet). Blender 5.0 + 5.1 on Linux, ruff, `extension validate`, headless suite.
- [ ] GUI tests (`scripts/test.py --gui`) under `xvfb` in CI.
- [ ] Cache the Blender download; upload the generated fixture add-on and screenshots as artifacts on failure.
- [ ] Code-quality job for generated add-ons (see 1).

## 6. Building and releasing

- [ ] One version source (manifest) and a release script: bump version, changelog entry, `blender --command extension build`, tag.
- [ ] GitHub release with the zip; decide on extensions.blender.org submission for Serpens itself (it must pass the same guidelines: e.g. `log_overlay.py` writes to `bpy.app.driver_namespace` at import time, MCP server needs the `network` permission and an `online_access` check if it ever goes beyond localhost).
- [ ] `scripts/dev.py` / `build.py` cleanup (dev loop could symlink the source like the tests instead of rebuilding a zip).
- [ ] Website deploy as part of the release; docs screenshots regenerated (`scripts/docs_screenshots.py`).

## 7. MCP server

- [ ] Update the tools to the new node API: socket keys instead of indices/names, flow socket `kind`, references by id, node code from the last build (`compiler.node_lines`), `mark_dirty()`.
- [ ] Tests for the tools (create nodes, link, set properties, read code) - currently only the security checks are tested.
- [ ] Optional bearer token, a timeout that doesn't run queued calls after the client gave up, split `tools.py` (1400 lines) into read/write modules.
- [ ] Docs page for using it with Claude Code / Codex.

## 8. Log overlay

- [ ] Move the import-time `driver_namespace` write into `register()`; the overlay is fed by `lib.logger` listeners and the `sn_print` helper.
- [ ] Show load and runtime errors (core/errors) with a "go to node" action; clear entries per rebuild.
- [ ] Settings (font size, on/off) per user preference instead of per scene.

## 9. v3 parity (after the code quality work)

Add To Panel / Menu, modal operators, timers (run with delay / intervals), keymaps/shortcuts, Report, loops (repeat, break), UI lists, popovers/pie menus, inline Python line, file and string utility nodes. See the v3 comparison in the session notes.

## 10. Smaller things

- [ ] Addon settings live on `scene.sna`: multi-scene files have one addon per scene. Decide whether settings move to the window manager / a file-level ID.
- [ ] "Save As" copies keep the addon uid; renaming the copy removes the original's generated folder (persistence).
- [ ] Per-tree compile caching if large files get slow (currently ~40 ms for 300 nodes).
- [ ] `normalize_indents` in `lib/code_format.py` is unused now.
