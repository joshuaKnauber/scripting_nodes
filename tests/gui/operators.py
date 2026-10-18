"""A modal operator (Invoke Type Modal, with a timer) runs its Modal flow on
timer events until a Return node finishes it, then its End flow; Event Info
reads the events; a UI List
draws in a sidebar panel.

Runs inside GUI Blender via `python scripts/test.py --gui`. Prints
"GUI TEST PASSED" or "GUI TEST FAILED: <reason>" and quits.
"""

import ast
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


def build():
    bpy.context.scene.sna.addon.addon_name = "Operator GUI"
    tree = helpers.new_tree("Operators")
    modal = add(tree, "SNA_Node_Operator", invoke_type="MODAL", modal_timer=0.05)
    modal.socket("label").value = "Count"
    count = add(
        tree,
        "SNA_Node_PythonStatement",
        code="context.scene['ticks'] = context.scene.get('ticks', 0) + 1",
    )
    enough = add(tree, "SNA_Node_PythonExpression", code="context.scene['ticks'] >= 3")
    branch = add(tree, "SNA_Node_IfElse")
    done = add(tree, "SNA_Node_OperatorReturn")
    ended = add(tree, "SNA_Node_PythonStatement", code="context.scene['ended'] = 1")
    info = add(tree, "SNA_Node_EventInfo")
    store = add(
        tree,
        "SNA_Node_PythonStatement",
        code="context.scene['event'] = repr((kind, tuple(mouse), shift))",
    )
    helpers.flush()
    helpers.link(tree, modal.outputs["event"], info.socket("event"))
    for name, key in (("kind", "type"), ("mouse", "mouse_region"), ("shift", "shift")):
        helpers.link(tree, info.outputs[key], store.socket("name_" + name))
    helpers.link(tree, modal.outputs["modal"], store.inputs[0])
    helpers.link(tree, store.outputs[0], count.inputs[0])
    helpers.link(tree, count.outputs[0], branch.inputs[0])
    helpers.link(tree, enough.outputs[0], branch.socket("condition"))
    helpers.link(tree, branch.outputs["then"], done.inputs[0])
    helpers.link(tree, modal.outputs["end"], ended.inputs[0])

    index = helpers.add_property("Index", "INTEGER")
    panel = add(tree, "SNA_Node_Panel", panel_category="Item")
    ui_list = add(tree, "SNA_Node_UIList")
    objects = add(tree, "SNA_Node_BlendData", path_root="DATA", path="objects")
    helpers.flush()
    helpers.link(tree, panel.outputs["body"], ui_list.inputs[0])
    helpers.link(tree, objects.outputs[0], ui_list.socket("items"))
    helpers.pick_property(ui_list, helpers.prop(index.id))
    helpers.flush()
    return modal


def step():
    try:
        s = state["step"]
        state["step"] += 1
        errors = helpers.sn("src.core.errors")
        if s == 0:
            helpers.enable_addon()
            modal = build()
            check(errors.addon_error is None, f"addon error: {errors.addon_error}")
            check(
                dict(errors.node_errors) == {},
                f"node errors: {dict(errors.node_errors)}",
            )
            window = bpy.context.window_manager.windows[0]
            area = next(a for a in window.screen.areas if a.type == "VIEW_3D")
            area.spaces.active.show_region_ui = True
            region = next(r for r in area.regions if r.type == "WINDOW")
            namespace, op = modal.operator_idname.split(".")
            with bpy.context.temp_override(window=window, area=area, region=region):
                result = getattr(getattr(bpy.ops, namespace), op)("INVOKE_DEFAULT")
            check(result == {"RUNNING_MODAL"}, f"didn't start: {result}")
        elif s == 1:
            scene = bpy.context.scene
            check(scene.get("ticks") == 3, f"ticks: {scene.get('ticks')}")
            check(scene.get("ended") == 1, "End didn't run")
            kind, mouse, shift = ast.literal_eval(scene.get("event"))
            # the last event the modal saw: a timer, or the mouse if it moved
            # over the window meanwhile
            check(
                kind.startswith("TIMER") or kind.endswith("MOUSEMOVE"),
                f"event type: {kind}",
            )
            check(len(mouse) == 2 and shift is False, f"event: {mouse}, {shift}")
            check(
                dict(errors.runtime_errors) == {},
                f"runtime errors: {dict(errors.runtime_errors)}",
            )
            print("GUI TEST PASSED")
            bpy.ops.wm.quit_blender()
            return None
    except Exception:
        traceback.print_exc()
        print("GUI TEST FAILED: " + traceback.format_exc().strip().splitlines()[-1])
        bpy.ops.wm.quit_blender()
        return None
    return 1.5


bpy.app.timers.register(step, first_interval=1.0)
