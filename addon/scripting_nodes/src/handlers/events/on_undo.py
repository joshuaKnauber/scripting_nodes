import bpy
from bpy.app.handlers import persistent

from ...core import scheduler


@persistent
def on_undo_redo(*args):
    # Undo restores node data (including cached code) to an older state; the
    # files on disk may not match it anymore. Rebuild from the graph.
    scheduler.request_full()


def register():
    bpy.app.handlers.undo_post.append(on_undo_redo)
    bpy.app.handlers.redo_post.append(on_undo_redo)


def unregister():
    bpy.app.handlers.undo_post.remove(on_undo_redo)
    bpy.app.handlers.redo_post.remove(on_undo_redo)
