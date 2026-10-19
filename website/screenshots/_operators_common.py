"""Shared helpers of the operators and events screenshots."""

import bpy
import helpers


def add(tree, idname, location, **settings):
    node = helpers.add_node(tree, idname, location)
    for name, value in settings.items():
        setattr(node, name, value)
    return node


def blender_operator(idname):
    """The picker text of a Blender operator ("Add Cube  [mesh.primitive_cube_add]")."""
    operator_call = helpers.sn("src.nodes._operator_call")
    return next(
        display
        for display, bl_idname in operator_call.blender_operator_choices()
        if bl_idname == idname
    )


def area_of(context, area_type):
    window = context.window_manager.windows[0]
    areas = [a for a in window.screen.areas if a.type == area_type]
    return window, max(areas, key=lambda a: a.width * a.height)


def hide_node_sidebar(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False


def later(function, delay=1.5):
    """Run `function()` once the driver has framed the nodes."""

    def run():
        try:
            function()
        except Exception:  # shows up in the scenario's output
            import traceback

            traceback.print_exc()
        return None

    bpy.app.timers.register(run, first_interval=delay)


def invoke_in(context, area_type, idname, mouse=None, delay=1.5, **props):
    """Start operator `idname` ("mod.name") from the interface of the biggest
    `area_type` area, after `delay` seconds. `mouse`: (x, y) in the area,
    fractions, where popups open."""
    window, area = area_of(context, area_type)
    region = next(r for r in area.regions if r.type == "WINDOW")
    if mouse is not None:
        window.cursor_warp(
            area.x + int(area.width * mouse[0]), area.y + int(area.height * mouse[1])
        )

    def run():
        namespace, name = idname.split(".")
        operator = getattr(getattr(bpy.ops, namespace), name)
        with bpy.context.temp_override(window=window, area=area, region=region):
            operator("INVOKE_DEFAULT", **props)

    later(run, delay)


def zoom_in(context, steps=1, delay=2.3):
    """Zoom the node editor in after the driver has framed all nodes
    (view_all leaves a wide margin)."""
    window, area = area_of(context, "NODE_EDITOR")
    region = next(r for r in area.regions if r.type == "WINDOW")

    def zoom():
        bpy.context.preferences.view.smooth_view = 0  # no animation
        with bpy.context.temp_override(window=window, area=area, region=region):
            for _ in range(steps):
                bpy.ops.view2d.zoom_in()

    later(zoom, delay)
