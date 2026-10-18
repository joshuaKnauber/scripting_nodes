"""Scripts of the add-on: an operator runs arrange.py, a panel draws with
selection_info.py. Node editor, the script in a Text Editor and the
generated panel in the 3D viewport.

Set SN_SAVE_BLEND to also save the file there."""

import os

import bpy
import helpers

LAYOUT = "split"
SIDEBAR_TAB = "Object Tools"

ARRANGE = '''import bpy


def run(context, spacing: float = 2.5, axis: int = 0) -> int:
    """Line up the selected objects."""
    objects = sorted(context.selected_objects, key=lambda o: o.name)
    for i, obj in enumerate(objects):
        obj.location[axis] = i * spacing
    count = len(objects)
    return count


def remember_file(*args):
    print("Saved", bpy.data.filepath)


def register():
    bpy.app.handlers.save_post.append(remember_file)


def unregister():
    bpy.app.handlers.save_post.remove(remember_file)
'''

SELECTION_INFO = '''def run(layout, context):
    """How many objects the operator will arrange."""
    count = len(context.selected_objects)
    layout.label(text=f"{count} objects selected", icon="RESTRICT_SELECT_OFF")
'''


def text(name, body):
    text = bpy.data.texts.new(name)
    text.write(body)
    return text


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    scene = bpy.context.scene
    for i in range(3):
        bpy.ops.mesh.primitive_monkey_add(location=(0, i * 3 - 3, 0), size=0.8)
    for obj in scene.objects:
        obj.select_set(obj.type == "MESH" and obj.name != "Cube")
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"])

    tree = helpers.new_tree("Object Tools")
    op = helpers.add_node(tree, "SNA_Node_Operator", (-700, 260))
    op.inputs["Label"].value = "Arrange Objects"
    arrange = helpers.add_node(tree, "SNA_Node_ScriptFunction", (-380, 300))
    arrange.script_id = helpers.add_script(text("arrange.py", ARRANGE)).id
    arrange.function_name = "run"
    helpers.flush()
    arrange.socket("spacing").value = 3.0
    log = helpers.add_node(tree, "SNA_Node_Print", (-60, 260))
    helpers.link(tree, op.outputs["Execute"], arrange.inputs[0])
    helpers.link(tree, arrange.outputs[0], log.inputs[0])
    helpers.link(tree, arrange.outputs["Count"], log.inputs[1])

    panel = helpers.add_node(tree, "SNA_Node_Panel", (-700, -120))
    panel.inputs["Label"].value = "Object Tools"
    panel.panel_category = "Object Tools"
    info = helpers.add_node(tree, "SNA_Node_ScriptFunction", (-380, -120))
    info.script_id = helpers.add_script(text("selection_info.py", SELECTION_INFO)).id
    info.function_name = "run"
    helpers.flush()
    button = helpers.add_node(tree, "SNA_Node_Button", (-60, -120))
    helpers.link(tree, panel.outputs["Draw"], info.inputs[0])
    helpers.link(tree, info.outputs[0], button.inputs[0])
    helpers.flush()
    helpers.point(button, "operator_sn", op)
    button.socket("label").value = "Arrange Objects"
    helpers.flush()
    return tree


def after(context):
    window = context.window_manager.windows[0]
    view = max(
        (a for a in window.screen.areas if a.type == "VIEW_3D"),
        key=lambda a: a.x,
    )
    region = next(r for r in view.regions if r.type == "WINDOW")
    with context.temp_override(window=window, area=view, region=region):
        bpy.ops.screen.area_split(direction="HORIZONTAL", factor=0.45)
    views = [a for a in window.screen.areas if a.type == "VIEW_3D"]
    bottom = min(views, key=lambda a: a.y)
    bottom.type = "TEXT_EDITOR"
    bottom.spaces.active.text = bpy.data.texts["arrange.py"]
    bottom.spaces.active.show_line_numbers = True
    bottom.spaces.active.show_syntax_highlight = True
    bottom.spaces.active.top = 0
    for area in window.screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.show_region_ui = True
        elif area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False

    # click the generated operator: the script lines the monkeys up along X
    tree = bpy.data.node_groups["Object Tools"]
    op = next(n for n in tree.nodes if n.bl_idname == "SNA_Node_Operator")
    namespace, name = op.sn_name("idname").split(".")
    print("ARRANGE:", getattr(getattr(bpy.ops, namespace), name)())
    print("LOCATIONS:", [tuple(o.location) for o in context.selected_objects])

    path = os.environ.get("SN_SAVE_BLEND")
    if path:
        bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
