"""View tweaks that have to run after the driver framed the nodes
(tests/visual/driver.py frame_all, run several times): zooming in, as view_all
leaves wide margins around a tree."""

import gc

import bpy


def _node_area(context):
    window = context.window_manager.windows[0]
    area = max(
        (a for a in window.screen.areas if a.type == "NODE_EDITOR"),
        key=lambda a: a.width * a.height,
    )
    return window, area


def after_framing(callback):
    """Run `callback()` after each of the driver's framing passes."""
    # the driver runs as a script, not a module: find its globals
    driver = next(
        (
            f.__globals__
            for f in gc.get_objects()
            if getattr(f, "__name__", "") == "frame_all"
            and "show_tree" in getattr(f, "__globals__", {})
        ),
        None,
    )
    if driver is None:
        return
    frame_all = driver["frame_all"]

    def framed(zoom_out=0):
        frame_all(zoom_out)
        callback()

    driver["frame_all"] = framed


def zoom_in(context, steps=2, hide_sidebar=True):
    window, area = _node_area(context)
    if hide_sidebar:
        area.spaces.active.show_region_ui = False
    region = next(r for r in area.regions if r.type == "WINDOW")
    context.preferences.view.smooth_view = 0

    def run():
        with context.temp_override(window=window, area=area, region=region):
            for _ in range(steps):
                bpy.ops.view2d.zoom_in()
        region.tag_redraw()

    after_framing(run)
