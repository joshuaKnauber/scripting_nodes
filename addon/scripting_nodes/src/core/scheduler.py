"""The single owner of "something changed -> regenerate -> compile -> reload".

Everything that can change generated code only *requests* work here:

    request_node(node)   a node's properties/sockets changed
    request_tree(tree)   links/nodes of a tree changed
    request_full()       file load, undo/redo, addon settings, renames, ...

Nothing compiles or reloads inside RNA update callbacks. A persistent timer
calls `flush()`, which runs the whole pipeline once:

    1. integrity  - init new trees, make tree/node ids unique, run versioning
    2. references - sync the scene.sna reference collections (picker lists)
    3. regenerate - re-run generate() on requested nodes, propagating to
                    neighbours and referencing nodes until the code is stable
    4. compile    - build every file of the addon from the node code (pure)
    5. apply      - write changed files and reload the addon transactionally

Pending work is stored as ids (never bpy objects), so undo or file loads can't
leave dangling pointers behind. `flush()` never raises; errors are logged and
shown in the UI.
"""

from collections import deque
import time

import bpy

from ..lib.logger import fmt_duration, log, log_if
from ..lib.screen import redraw_all
from ..lib.trees import scripting_node_trees, sn_nodes
from . import compiler, errors, integrity, references, runtime

TICK_SECONDS = 0.1
# A node regenerating more often than this in one flush is part of a feedback
# loop (generate() output keeps changing); stop instead of hanging Blender.
MAX_VISITS_PER_NODE = 100

_pending_nodes: set[str] = set()
_pending_trees: set[int] = set()
_full = True  # first flush after register always rebuilds everything
_flushing = False
_queue = None  # _OrderedQueue while a flush regenerates


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------


def request_node(node):
    """Regenerate `node` (and whatever depends on it) on the next flush."""
    if _queue is not None:
        # Inside a flush (e.g. on_ref_change): handle in the same pass
        _queue.append(node)
        return
    if node.id:
        _pending_nodes.add(node.id)


def request_tree(tree):
    """Regenerate every node of `tree` on the next flush."""
    if tree is not None and not _flushing:
        _pending_trees.add(tree.session_uid)


def request_full():
    """Rebuild everything from the graph on the next flush."""
    global _full
    _full = True


def has_pending() -> bool:
    return _full or bool(_pending_nodes) or bool(_pending_trees)


def _take_pending():
    global _full
    full, node_ids, tree_uids = _full, set(_pending_nodes), set(_pending_trees)
    _full = False
    _pending_nodes.clear()
    _pending_trees.clear()
    return full, node_ids, tree_uids


# ---------------------------------------------------------------------------
# Flush
# ---------------------------------------------------------------------------


def flush():
    """Run all pending work now. Safe to call any time; never raises."""
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
    full, node_ids, tree_uids = _take_pending()
    dev = bpy.context.scene.sna.dev
    trees = scripting_node_trees()

    if full:
        integrity.ensure(trees)
    for tree in trees:
        if full or tree.session_uid in tree_uids:
            tree.update_reroutes()
    references.sync(trees)

    if full:
        start = [node for tree in trees for node in sn_nodes(tree)]
    else:
        start = []
        for tree in trees:
            whole_tree = tree.session_uid in tree_uids
            for node in sn_nodes(tree):
                if whole_tree or node.id in node_ids:
                    start.append(node)

    t0 = time.perf_counter()
    regenerated = regenerate(start)
    t1 = time.perf_counter()
    files = compiler.compile_addon()
    t2 = time.perf_counter()
    reloaded = runtime.apply(files)
    t3 = time.perf_counter()

    log_if(
        dev.log_tree_rebuilds,
        "INFO",
        f"{'full' if full else 'incremental'} update: {regenerated} node(s) "
        f"regenerated in {fmt_duration(t1 - t0)}, compile {fmt_duration(t2 - t1)}",
    )
    log_if(
        dev.log_reload_times and reloaded,
        "INFO",
        f"reloaded addon in {fmt_duration(t3 - t2)}",
    )


def regenerate(start) -> int:
    """Regenerate `start` nodes and propagate changes until code is stable.

    Nodes are processed in dependency order (data producers before
    consumers, downstream program nodes before the upstream nodes embedding
    their code), so most nodes run once. When a node's code changes, the
    nodes reading it (`dependent_nodes()` and nodes referencing it by id) are
    queued again. Returns the number of generate() calls.
    """
    global _queue
    dependents = references.dependents_index()
    visits: dict[int, int] = {}
    warned = set()
    count = 0
    _queue = _OrderedQueue(dependency_order(start))
    try:
        while _queue:
            node = _queue.popleft()
            key = node.as_pointer()
            visits[key] = visits.get(key, 0) + 1
            if visits[key] > MAX_VISITS_PER_NODE:
                if key not in warned:
                    warned.add(key)
                    log("WARNING", f"'{node.name}' keeps changing its code, skipped")
                continue
            count += 1
            changes = node.regenerate()
            if not any(changes):
                continue
            for other in node.dependent_nodes(changes):
                _queue.append(other)
            for other in dependents.get(node.id, ()):
                other.on_ref_change(node)
    finally:
        _queue = None
    return count


class _OrderedQueue:
    """FIFO without duplicates (a node waiting in the queue isn't added twice)."""

    def __init__(self, nodes=()):
        self._items = deque()
        self._keys = set()
        for node in nodes:
            self.append(node)

    def append(self, node):
        key = node.as_pointer()
        if key not in self._keys:
            self._keys.add(key)
            self._items.append(node)

    def popleft(self):
        node = self._items.popleft()
        self._keys.discard(node.as_pointer())
        return node

    def __bool__(self):
        return bool(self._items)


def dependency_order(nodes):
    """`nodes` sorted so each comes after the nodes its code reads (DFS
    post-order). Cycles (e.g. a loop body using the loop's item) are broken
    arbitrarily; the propagation in regenerate() fixes up the rest."""
    wanted = {node.as_pointer(): node for node in nodes}
    done, active, order = set(), set(), []
    for root in nodes:
        stack = [(root, iter(root.code_dependencies()))]
        if root.as_pointer() in done:
            continue
        active.add(root.as_pointer())
        while stack:
            node, deps = stack[-1]
            for dep in deps:
                key = dep.as_pointer()
                if key in wanted and key not in done and key not in active:
                    active.add(key)
                    stack.append((dep, iter(dep.code_dependencies())))
                    break
            else:
                stack.pop()
                key = node.as_pointer()
                active.discard(key)
                done.add(key)
                order.append(node)
    return order


def regenerate_all():
    """Synchronously regenerate every node (used by export in build mode)."""
    trees = scripting_node_trees()
    references.sync(trees)
    return regenerate([n for t in trees for n in sn_nodes(t)])


# ---------------------------------------------------------------------------
# Timer
# ---------------------------------------------------------------------------


def _context_ready() -> bool:
    scene = getattr(bpy.context, "scene", None)
    return scene is not None and hasattr(scene, "sna")


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


def _run_watchers():
    for fn in list(_watchers):
        try:
            fn()
        except Exception as exc:
            log("ERROR", f"Watcher {getattr(fn, '__name__', fn)} failed: {exc}")


def _tick():
    global _ticks
    _ticks += 1
    if _ticks % WATCH_EVERY == 0 and _context_ready():
        _run_watchers()
    if has_pending():
        flush()
    return TICK_SECONDS


def register():
    global _full
    _full = True
    _pending_nodes.clear()
    _pending_trees.clear()
    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=TICK_SECONDS, persistent=True)


def unregister():
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
