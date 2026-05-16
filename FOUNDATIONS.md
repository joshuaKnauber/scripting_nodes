# Foundations of Scripting Nodes

A map of the core architecture: nodes, sockets, code generation, dev vs prod, registration.

## Core entities

**ScriptingNodeTree** (`features/node_tree/node_tree.py`) — a Blender `NodeTree` subclass. Holds an `id`, `is_dirty`, `pause_updates`. Tracks link add/remove via `update()` to forward `ntree_link_created/removed()` to nodes, and reroute socket types.

**ScriptingBaseNode** (`features/nodes/base_node.py`) — every node has:
- a unique `id` (short UUID, regenerated on copy)
- four output buffers: `code`, `code_global`, `code_register`, `code_unregister`
- a `generate()` method (subclass responsibility) that populates those buffers from current state
- a `_generate()` orchestrator that calls `generate()`, diffs buffers, propagates to upstream/downstream nodes, and flips `ntree.is_dirty`
- `sn_options` — flags like `ROOT_NODE` (event entry points)

**ScriptingBaseSocket** (`features/sockets/base_socket.py`) — two families:
- **DATA sockets** — `.eval()` returns a Python *expression string* (e.g. `"1.5 + 2"`); type conversion via `conversions.py` (165 pairs) inserts casts at mismatched links
- **PROGRAM sockets** — `.eval()` returns a Python *statement block*; outputs forward to downstream `to_socket().eval()`; inputs return either inlined node code (prod) or a dispatcher call (dev)

Recursion guard `_eval_stack` keyed on `node.id:name:is_output` prevents cycles. Reroutes are transparently skipped by `from_socket`/`to_socket`.

## The two evaluation modes

```
DATA socket eval (expression)              PROGRAM socket eval (statement)
─────────────────────────────              ───────────────────────────────
input unlinked   → _to_code()              input (dev)   → bpy.context.scene.sna
                   ("1", "''", ...)                       .execute('node_id', ...)
input linked     → from_socket.eval()      input (prod)  → normalize_indents(node.code)
                   + get_conversion()      output linked → to_socket.eval()
output           → self.code               output free   → ""
```

`build_with_production_code` (a scene-level flag) chooses the program-socket input path. That single flag is the dev/prod hinge.

## Data flow at a glance

```
┌─────────────────┐     graph edit       ┌─────────────────┐
│  Blender NTree  │ ───── update() ────► │  ntree.is_dirty │
│  (user editing) │                       │     = True      │
└─────────────────┘                       └────────┬────────┘
                                                   │
                       ┌───────────────────────────▼──────────────────────┐
                       │  watcher.py (timer, 0.25s active / 1s idle / 2s  │
                       │  prod)  →  generator.generate_addon()            │
                       └───────────────────────────┬──────────────────────┘
                                                   │
                                                   ▼
                       per node:  _generate() → fills code/code_global/
                                                code_register/code_unregister
                                                   │
                                                   ▼
                       per dirty tree: assemble {tree}.py
                       │  imports + code_global
                       │  root-node code (event handlers)
                       │  def register(): all code_register
                       │  def unregister(): all code_unregister
                                                   │
                                                   ▼
                       write to {addon_path}/addon/{tree}.py
                                                   │
                                                   ▼
                       reload_addon(module_name) via addon_utils
```

## Generated-addon layout (multiple files)

Every export — dev install or prod zip — produces the same shape:

```
generated_addon/
├── __init__.py            ← module alias + auto_load.init/register/unregister
├── auto_load.py           ← copy of SN's auto_load (topo-sorted reg)
├── blender_manifest.toml
└── addon/
    ├── __init__.py        ← empty marker
    ├── tree_a.py          ← one ScriptingNodeTree → one .py
    └── tree_b.py
```

Each `tree_x.py` is structured the same way:

```python
import bpy
# <code_global for every ROOT_NODE>
# <code for every ROOT_NODE>              ← event handlers, panel classes, etc.

def register():
    # <code_register concatenated>

def unregister():
    # <code_unregister concatenated>
```

**ROOT_NODE** is the key concept: only nodes flagged ROOT_NODE emit top-level statements. Everything else is reachable transitively — their `code` is pulled in via `_eval_program()` when a root traverses its outputs.

## Dev vs prod, end-to-end

|                         | Dev                                                                   | Prod                                                          |
| ----------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------- |
| Program socket inputs   | `bpy.context.scene.sna.execute('node_id', globals(), locals())`       | `normalize_indents(node.code)` inlined                        |
| Dispatcher              | `SNA_Settings.execute()` in `settings_properties.py` → `node._execute()` | (none — no dispatcher in shipped output)                   |
| Watcher cadence         | 0.25s active / 1s idle                                                | 2s                                                            |
| Formatting              | none                                                                  | `autopep8`                                                    |
| Reload                  | `addon_utils.disable/enable` on each generate                         | `scripts/build.py` zips and validates                        |
| Why two modes           | Editing a single node only needs that node re-evaluated; the dispatcher routes runtime back into SN's live data | Shipped addons can't depend on SN; everything must be inlined |

## Registration plumbing

`auto_load.py` lives both **in SN itself** and **in every generated addon** (copied verbatim). It:
1. Walks submodules
2. Inspects classes for `bpy.types.X` ancestry + type annotations + `bl_parent_id`
3. Topologically sorts them (PropertyGroup before Operator before Panel that references them)
4. Registers in that order; unregisters in reverse

This is what makes "just drop a Python file in a category folder" work — no manual `register()` wiring.

## Observations on depth

**Deep foundations** (small interface, large behaviour):
- `ScriptingBaseSocket.eval()` — graph traversal, recursion guard, type conversion, dev/prod switch all behind one method
- `auto_load` — one call, full dependency resolution
- The per-node `code_*` buffer convention — four strings, completely general

**Worth poking at**:
- Dirty-bit lives both globally on the scene *and* per-tree
- The dev dispatcher mixes runtime concerns into a scene PropertyGroup
- The watcher's cadence logic is hand-tuned
- "Is the generated module a single artifact or N files?" is decided implicitly by node-tree count rather than a deliberate seam
