"""Make Group (Ctrl+G) and Ungroup (Ctrl+Alt+G) in a real node editor.

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


def editor(tree):
    """Override for a node editor showing `tree`."""
    window = bpy.context.window_manager.windows[0]
    area = max(window.screen.areas, key=lambda a: a.width * a.height)
    area.type = "NODE_EDITOR"
    space = area.spaces.active
    space.tree_type = "ScriptingNodeTree"
    if tree is not None:
        space.node_tree = tree
    region = next(r for r in area.regions if r.type == "WINDOW")
    return bpy.context.temp_override(
        window=window, area=area, region=region, space_data=space
    )


def linked(from_socket, to_socket):
    return any(link.to_socket == to_socket for link in from_socket.links)


def nodes(tree, idname):
    return [n for n in tree.nodes if n.bl_idname == idname]


def step():
    try:
        s = state["step"]
        state["step"] += 1
        if s == 0:
            helpers.enable_addon()
            bpy.context.scene.sna.addon.addon_name = "Group Test"
            tree = helpers.new_tree("Main")
            trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-400, 0))
            first = helpers.add_node(tree, "SNA_Node_Print", (0, 0))
            text = helpers.add_node(tree, "SNA_Node_String", (-200, -200))
            text.value = "grouped"
            last = helpers.add_node(tree, "SNA_Node_Print", (300, 0))
            helpers.link(tree, trigger.outputs[0], first.inputs[0])
            helpers.link(tree, text.outputs[0], first.inputs["text"])
            helpers.link(tree, first.outputs[0], last.inputs[0])
            helpers.flush()
            state.update(first_id=first.id, first=first.name, last=last.name)
            for node in tree.nodes:
                node.select = node in (first, text)
            with editor(tree):
                check(bpy.ops.sna.make_group() == {"FINISHED"}, "make group failed")
        elif s == 1:
            helpers.flush()
            tree = bpy.data.node_groups["Main"]
            group = next(t for t in bpy.data.node_groups if t != tree)
            check(group.is_function, "new tree has no interface")
            calls = nodes(tree, "SNA_Node_Group")
            check(len(calls) == 1 and calls[0].node_tree == group, "no group node")
            call = calls[0]
            check(
                sorted(n.bl_idname for n in tree.nodes)
                == ["SNA_Node_Group", "SNA_Node_Print", "SNA_Node_Trigger"],
                f"nodes left in main: {[n.name for n in tree.nodes]}",
            )
            check(
                sorted(n.bl_idname for n in group.nodes)
                == [
                    "NodeGroupInput",
                    "NodeGroupOutput",
                    "SNA_Node_Print",
                    "SNA_Node_String",
                ],
                f"nodes in group: {[n.name for n in group.nodes]}",
            )
            check(group.nodes[state["first"]].id == state["first_id"], "id changed")
            trigger = nodes(tree, "SNA_Node_Trigger")[0]
            last = tree.nodes[state["last"]]
            check(linked(trigger.outputs[0], call.inputs[0]), "trigger -> group")
            check(linked(call.outputs[0], last.inputs[0]), "group -> print")
            check(helpers.sn("src.core.errors").addon_error is None, "addon error")
            source = helpers.tree_source(tree)
            check(f"{group.function_name}(" in source, "group not called")
            check("'grouped'" in helpers.tree_source(group), "group body missing")
            for node in tree.nodes:
                node.select = node == call
            with editor(tree):
                check(bpy.ops.sna.ungroup() == {"FINISHED"}, "ungroup failed")
        elif s == 2:
            helpers.flush()
            tree = bpy.data.node_groups["Main"]
            check(not nodes(tree, "SNA_Node_Group"), "group node still there")
            prints = nodes(tree, "SNA_Node_Print")
            strings = nodes(tree, "SNA_Node_String")
            check(len(prints) == 2 and len(strings) == 1, "nodes not restored")
            trigger = nodes(tree, "SNA_Node_Trigger")[0]
            last = tree.nodes[state["last"]]
            first = next(p for p in prints if p != last)
            check(linked(trigger.outputs[0], first.inputs[0]), "trigger -> print")
            check(linked(first.outputs[0], last.inputs[0]), "print -> print")
            check(linked(strings[0].outputs[0], first.inputs["text"]), "string link")
            check(helpers.sn("src.core.errors").addon_error is None, "addon error")
            check("'grouped'" in helpers.tree_source(tree), "ungrouped code missing")
            print("GUI TEST PASSED")
            bpy.ops.wm.quit_blender()
            return None
    except Exception:
        traceback.print_exc()
        print("GUI TEST FAILED: " + traceback.format_exc().strip().splitlines()[-1])
        bpy.ops.wm.quit_blender()
        return None
    return 0.3


bpy.app.timers.register(step, first_interval=1.0)
