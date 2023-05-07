import bpy
import time
from ...utils.logging import log
from ...utils.redraw import redraw


_queue = []
_last_start_time = 0


def _process_queue():
    """ Process the first item in the queue and return the interval for the next call. """
    global _queue, _last_start_time
    if len(_queue) == 0:
        log(1, "Stop watching queue")
        redraw(all=True)
        bpy.context.scene.sn.last_generate_time = time.time() - _last_start_time
        return None

    log(0, "Processing queue", [node.name for node in _queue])
    while len(_queue) > 0:
        node_time = time.time()
        node = _queue.pop(0)
        log(0, "Processing", node.name)
        node.generate(bpy.context)
        node.last_generate_time = time.time() - node_time
    return 0.001


def _is_watching_queue():
    """ Returns if the queue is being processed. """
    return bpy.app.timers.is_registered(_process_queue)


def watch_queue():
    """ Start processing the queue and watch for new items until the queue is empty. """
    global _last_start_time
    if _is_watching_queue():
        return
    log(1, "Start watching queue")
    _last_start_time = time.time()
    bpy.app.timers.register(_process_queue)


def add_to_queue(node):
    """ Adds the given node to the queue for processing. """
    global _queue
    if len(_queue) == 0 or _queue[-1] != node:
        _queue.append(node)
        watch_queue()
