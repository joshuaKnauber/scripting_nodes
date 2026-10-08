"""The single owner of "something changed -> rebuild -> reload".

Everything that can change the generated code only *requests* a rebuild:

    request_node(node)   a node's properties/sockets changed
    request_tree(tree)   links/nodes of a tree changed
    request_full()       file load, undo/redo, addon settings, renames, ...

Nothing compiles or reloads inside RNA update callbacks. A persistent timer
calls `flush()`, which runs the pipeline once:

    1. integrity  - init new trees, unique tree/node ids, versioning (full only)
    2. sockets    - every node's sockets match its declaration
    3. references - rebuild the picker collections on scene.sna
    4. compile    - graph -> files (core/compiler.py, pure)
    5. apply      - write changed files, reload the addon (core/runtime.py)

Nodes store no generated code, so there's nothing that can go stale: what's
in the graph is what compiles. `flush()` never raises.
"""

import time

import bpy

from ..lib.logger import fmt_duration, log, log_if
from ..lib.screen import redraw_all
from ..lib.trees import scripting_node_trees, sn_nodes
from . import compiler, errors, functions, integrity, references, runtime

TICK_SECONDS = 0.1

_dirty = True
_full = True  # first flush after register checks everything
_flushing = False


def request_node(node):
    """Rebuild because `node` changed."""
    global _dirty
    _dirty = True


def request_tree(tree):
    """Rebuild because links or nodes of `tree` changed."""
    global _dirty
    _dirty = True


def request_full():
    """Rebuild and re-check the whole file (ids, versioning, sockets)."""
    global _dirty, _full
    _dirty = _full = True


def has_pending() -> bool:
    return _dirty or _full


def flush():
    """Run pending work now. Safe to call any time; never raises."""
    global _flushing
    if _flushing or not has_pending() or not _context_ready():
        return
    _flushing = True
    try:
        _flush()
    except Exception as exc:
        log("ERROR", "Scripting Nodes update failed:\n" + errors.format_exception(exc))
    finally:
        _flushing = False
    redraw_all()


def _flush():
    global _dirty, _full
    full = _full
    _dirty = _full = False
    dev = bpy.context.scene.sna.dev
    trees = scripting_node_trees()

    if full:
        integrity.ensure(trees)
    for tree in trees:
        tree.update_reroutes()
        if functions.sync_io_sockets(tree):
            tree.update()  # links may connect (or not) now
    # sockets can depend on other nodes (e.g. a Get Variable's type), so a
    # change may ripple once or twice
    for _ in range(3):
        if not any([node.sync_sockets() for t in trees for node in sn_nodes(t)]):
            break
    references.sync(trees)

    t0 = time.perf_counter()
    files = compiler.compile_addon(dev=True)
    t1 = time.perf_counter()
    reloaded = runtime.apply(files)
    t2 = time.perf_counter()
    # changes made above (socket syncing) request another flush; ignore them
    _dirty = False

    log_if(dev.log_tree_rebuilds, "INFO", f"compiled in {fmt_duration(t1 - t0)}")
    log_if(
        dev.log_reload_times and reloaded,
        "INFO",
        f"reloaded in {fmt_duration(t2 - t1)}",
    )


# ---------------------------------------------------------------------------
# Watchers
# ---------------------------------------------------------------------------

# Callables polled every WATCH_EVERY ticks to detect changes Blender doesn't
# report through RNA updates (e.g. edits to a Text datablock or an external
# file used by a Script node). They call request_node()/request_tree().
_watchers: list = []
WATCH_EVERY = 5
_ticks = 0


def add_watcher(fn):
    if fn not in _watchers:
        _watchers.append(fn)


def remove_watcher(fn):
    if fn in _watchers:
        _watchers.remove(fn)


def run_watchers():
    for fn in list(_watchers):
        try:
            fn()
        except Exception as exc:
            log("ERROR", f"Watcher {getattr(fn, '__name__', fn)} failed: {exc}")


# ---------------------------------------------------------------------------
# Timer
# ---------------------------------------------------------------------------


def _context_ready() -> bool:
    scene = getattr(bpy.context, "scene", None)
    return scene is not None and hasattr(scene, "sna")


def _tick():
    global _ticks
    _ticks += 1
    if _ticks % WATCH_EVERY == 0 and _context_ready():
        run_watchers()
    if has_pending():
        flush()
    return TICK_SECONDS


def register():
    request_full()
    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=TICK_SECONDS, persistent=True)


def unregister():
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
