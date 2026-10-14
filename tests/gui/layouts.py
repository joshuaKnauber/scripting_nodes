"""On Blender Change runs when the active object changes (bpy.msgbus only
notifies with an event loop), and a sidebar panel using every new layout
node and field style draws without errors.

Runs inside GUI Blender via `python scripts/test.py --gui`. Prints
"GUI TEST PASSED" or "GUI TEST FAILED: <reason>" and quits.
"""

import os
import sys
import traceback

import bpy

sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helpers  # noqa: E402

state = {"step": 0}


def check(condition, reason):
    if not condition:
        raise AssertionError(reason)


def add(tree, idname, **settings):
    node = helpers.add_node(tree, idname)
    for name, value in settings.items():
        setattr(node, name, value)
    return node


def chain(tree, start, nodes):
    for node in nodes:
        helpers.link(tree, start, node.inputs[0])
        start = next(s for s in node.outputs if s.identifier == "next")


def build():
    bpy.context.scene.sna.addon.addon_name = "Layout GUI"
    tree = helpers.new_tree("Layouts")

    # the active object changing marks the scene
    watch = add(tree, "SNA_Node_OnBlenderChange", path="view_layer.objects.active")
    mark = add(
        tree, "SNA_Node_PythonStatement", code="bpy.context.scene['changed'] = 1"
    )
    helpers.flush()
    helpers.link(tree, watch.outputs[0], mark.inputs[0])

    panel = add(tree, "SNA_Node_Panel", panel_category="Item")
    panel.socket("label").value = "Layout Test"
    blender = {"mode": "BLENDER"}
    nodes = [
        add(
            tree,
            "SNA_Node_TextField",
            path="scene.render.filepath",
            style="TEXTBOX",
            **blender,
        ),
        add(
            tree,
            "SNA_Node_TextField",
            path="scene.render.filepath",
            style="FIELD",
            **blender,
        ),
        add(
            tree,
            "SNA_Node_EnumMenu",
            path="scene.render.engine",
            expand=True,
            **blender,
        ),
        add(
            tree,
            "SNA_Node_EnumMenu",
            path="scene.render.engine",
            style="ICONS",
            **blender,
        ),
        add(
            tree,
            "SNA_Node_PointerField",
            path="scene.world",
            style="SELECTOR",
            **blender,
        ),
        add(tree, "SNA_Node_Split"),
        add(tree, "SNA_Node_Grid"),
        add(tree, "SNA_Node_Progress", progress_type="RING"),
        add(
            tree,
            "SNA_Node_OperatorMenu",
            mode="BLENDER",
            operator_blender="object.mode_set",
            enum_property="mode",
        ),
        add(
            tree,
            "SNA_Node_MenuContents",
            source="BLENDER",
            blender_menu="VIEW3D_MT_add",
        ),
        add(tree, "SNA_Node_LayoutState", operator_context="EXEC_DEFAULT"),
    ]
    helpers.flush()
    chain(tree, panel.outputs["body"], nodes)
    each = add(tree, "SNA_Node_DrawForEach")
    helpers.link(tree, nodes[6].outputs["content"], each.inputs[0])  # in the grid
    objects = add(tree, "SNA_Node_BlendData", path_root="DATA", path="objects")
    helpers.flush()
    helpers.link(tree, objects.outputs[0], each.socket("list"))
    pointer = add(tree, "SNA_Node_ContextData")
    label = add(tree, "SNA_Node_Label")
    helpers.link(tree, each.outputs["loop"], pointer.inputs[0])
    helpers.link(tree, each.outputs["item"], pointer.socket("data"))
    helpers.link(tree, pointer.outputs[0], label.inputs[0])
    helpers.link(tree, each.outputs["item"], label.socket("text"))
    helpers.flush()


def view3d():
    window = bpy.context.window_manager.windows[0]
    return next(a for a in window.screen.areas if a.type == "VIEW_3D")


def step():
    try:
        s = state["step"]
        state["step"] += 1
        errors = helpers.sn("src.core.errors")
        if s == 0:
            helpers.enable_addon()
            build()
            check(errors.addon_error is None, f"addon error: {errors.addon_error}")
            check(
                dict(errors.node_errors) == {},
                f"node errors: {dict(errors.node_errors)}",
            )
            area = view3d()
            area.spaces.active.show_region_ui = True
            area.tag_redraw()
            layer = bpy.context.view_layer
            layer.objects.active = bpy.data.objects["Camera"]
        elif s == 1:
            check(bpy.context.scene.get("changed") == 1, "msgbus didn't notify")
            check(
                dict(errors.runtime_errors) == {},
                f"drawing failed: {dict(errors.runtime_errors)}",
            )
            print("GUI TEST PASSED")
            bpy.ops.wm.quit_blender()
            return None
    except Exception:
        traceback.print_exc()
        print("GUI TEST FAILED: " + traceback.format_exc().strip().splitlines()[-1])
        bpy.ops.wm.quit_blender()
        return None
    return 1.0


bpy.app.timers.register(step, first_interval=1.0)
