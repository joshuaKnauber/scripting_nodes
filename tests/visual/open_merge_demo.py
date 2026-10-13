"""Opens GUI Blender on a demo of the merged v4 work (run by
scripts/open_example.py tests/visual/open_merge_demo.py).

One add-on, "Merge Demo", with a frame per feature:
  - Script node: arrange.py becomes a module of the add-on, the node calls
    its run(); inputs and outputs come from the signature
  - Blend Data: one path node with typed outputs, chained from the active
    object; Set Property / fields in Blender mode follow a path
  - Properties as lists: the add-on property "Spacing" (sidebar, Addon Data)
    feeds the script and is drawn by a Number Field in Custom mode
  - References: Buttons pick operators and Get/Set Variable pick a variable
    in search fields; the second tree reads the variable from another tree
    and has a Set Variable whose variable was deleted (red field)
"""

import os
import sys
import traceback

import bpy

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TESTS_DIR)

import helpers  # noqa: E402

OUTPUT = sys.argv[sys.argv.index("--") + 1]

ARRANGE = '''import bpy


def run(context, spacing: float = 2.5) -> int:
    """Line up the selected objects along X."""
    objects = sorted(context.selected_objects, key=lambda o: o.name)
    for i, obj in enumerate(objects):
        obj.location.x = i * spacing
    count = len(objects)
    return count
'''


def frame(tree, label, location, color):
    node = tree.nodes.new("NodeFrame")
    node.label = label
    node.label_size = 28
    node.location = location
    node.use_custom_color = True
    node.color = color
    return node


def add(tree, idname, location, parent=None):
    node = helpers.add_node(tree, idname, location)
    if parent is not None:
        node.parent = parent
        node.location_absolute = location
    return node


def blend_data(tree, location, path, root="CONTEXT", parent=None):
    node = add(tree, "SNA_Node_BlendData", location, parent)
    node.path_root = root
    node.path = path
    return node


def build_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj)
    for i in range(4):
        bpy.ops.mesh.primitive_monkey_add(location=(0, i * 2.5 - 4, 0), size=0.8)
    bpy.ops.mesh.primitive_cube_add(location=(0, 6, 0))
    cube = bpy.context.active_object
    cube.name = "Cube"
    cube.modifiers.new("Bevel", "BEVEL")
    for obj in bpy.context.scene.objects:
        obj.select_set(obj.name.startswith("Suzanne"))
    bpy.context.view_layer.objects.active = bpy.data.objects["Suzanne"]


def build():
    build_scene()
    bpy.context.scene.sna.addon.addon_name = "Merge Demo"
    tree = helpers.new_tree("Merge Demo")
    other = helpers.new_tree("Other Tree")
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731

    spacing = helpers.add_property("Spacing", "FLOAT", default_float=3.0)
    spacing_id = spacing.id

    # -- references: the variable the others point at ------------------------
    refs = frame(
        tree,
        "References: search fields, used by (sidebar)",
        (-1500, 760),
        (0.25, 0.2, 0.3),
    )
    arranged = add(tree, "SNA_Node_GlobalVariable", (-1450, 700), refs)
    arranged.label = "Arranged"
    arranged.data_type = "ScriptingIntegerSocket"

    # -- script node ----------------------------------------------------------
    script_frame = frame(
        tree,
        "Script node: arrange.py is a module, the node calls run()",
        (-1100, 760),
        (0.2, 0.28, 0.22),
    )
    arrange_op = add(tree, "SNA_Node_Operator", (-1050, 700), script_frame)
    arrange_op.socket("label").value = "Arrange Objects"
    text = bpy.data.texts.new("arrange.py")
    text.write(ARRANGE)
    script = add(tree, "SNA_Node_Script", (-750, 700), script_frame)
    script.text_block = text
    get_spacing = add(tree, "SNA_Node_GetProperty", (-1050, 450), script_frame)
    helpers.flush()
    helpers.pick_property(get_spacing, helpers.prop(spacing_id))
    set_arranged = add(tree, "SNA_Node_SetVariable", (-450, 700), script_frame)
    helpers.point(set_arranged, "var", arranged)
    log = add(tree, "SNA_Node_Print", (-200, 700), script_frame)
    helpers.flush()
    link(arrange_op.outputs["Execute"], script.inputs[0])
    link(get_spacing.outputs["Value"], script.socket("spacing"))
    link(script.outputs[0], set_arranged.inputs[0])
    link(script.outputs["Count"], set_arranged.socket("value"))
    link(set_arranged.outputs[0], log.inputs[0])
    link(script.outputs["Count"], log.inputs[1])

    # -- blend data -----------------------------------------------------------
    data_frame = frame(
        tree,
        "Blend Data: one path node, typed sockets",
        (-1500, 260),
        (0.2, 0.24, 0.32),
    )
    report_op = add(tree, "SNA_Node_Operator", (-1450, 200), data_frame)
    report_op.socket("label").value = "Report Active Object"
    active = blend_data(tree, (-1450, -50), "active_object", parent=data_frame)
    name = blend_data(tree, (-1150, -50), "name", root="INPUT", parent=data_frame)
    modifiers = blend_data(
        tree, (-1150, -250), "modifiers", root="INPUT", parent=data_frame
    )
    count = add(tree, "SNA_Node_CollectionLength", (-850, -250), data_frame)
    print_name = add(tree, "SNA_Node_Print", (-850, 200), data_frame)
    print_mods = add(tree, "SNA_Node_Print", (-600, 200), data_frame)
    show_name = add(tree, "SNA_Node_SetProperty", (-350, 200), data_frame)
    show_name.mode = "BLENDER"
    show_name.path = "active_object.show_name"
    helpers.flush()
    show_name.socket("value").value = True
    link(active.outputs[0], name.socket("data"))
    link(active.outputs[0], modifiers.socket("data"))
    link(modifiers.outputs[0], count.inputs[0])
    link(report_op.outputs["Execute"], print_name.inputs[0])
    link(name.outputs[0], print_name.inputs[1])
    link(print_name.outputs[0], print_mods.inputs[0])
    link(count.outputs[0], print_mods.inputs[1])
    link(print_mods.outputs[0], show_name.inputs[0])

    # -- panel: fields in Blender + Custom mode, buttons pick operators -------
    ui_frame = frame(
        tree,
        "Panel: Blender paths, add-on property, buttons",
        (-1500, -460),
        (0.3, 0.26, 0.18),
    )
    panel = add(tree, "SNA_Node_Panel", (-1450, -520), ui_frame)
    panel.socket("label").value = "Merge Demo"
    panel.panel_category = "Merge Demo"
    simplify = add(tree, "SNA_Node_Checkbox", (-1200, -520), ui_frame)
    simplify.mode = "BLENDER"
    simplify.path = "scene.render.use_simplify"
    bevel = add(tree, "SNA_Node_NumberField", (-950, -520), ui_frame)
    bevel.mode = "BLENDER"
    # what "Copy Data Path for Scripting Nodes" puts on the clipboard
    bevel.paste_path('bpy.data.objects["Cube"].modifiers["Bevel"].width')
    spacing_field = add(tree, "SNA_Node_NumberField", (-700, -520), ui_frame)
    helpers.flush()
    helpers.pick_property(spacing_field, helpers.prop(spacing_id))
    get_arranged = add(tree, "SNA_Node_GetVariable", (-450, -760), ui_frame)
    helpers.point(get_arranged, "var", arranged)
    label = add(tree, "SNA_Node_Label", (-450, -520), ui_frame)
    arrange_button = add(tree, "SNA_Node_Button", (-200, -520), ui_frame)
    report_button = add(tree, "SNA_Node_Button", (50, -520), ui_frame)
    helpers.point(arrange_button, "operator_sn", arrange_op)
    helpers.point(report_button, "operator_sn", report_op)
    helpers.flush()
    arrange_button.socket("label").value = "Arrange Objects"
    report_button.socket("label").value = "Report Active Object"
    link(panel.outputs["Interface"], simplify.inputs[0])
    link(simplify.socket("next", output=True), bevel.inputs[0])
    link(bevel.socket("next", output=True), spacing_field.inputs[0])
    link(spacing_field.socket("next", output=True), label.inputs[0])
    link(get_arranged.outputs[0], label.inputs["Label"])
    link(label.outputs[0], arrange_button.inputs[0])
    link(arrange_button.socket("next", output=True), report_button.inputs[0])

    # -- other tree: the variable from another tree, a deleted target ---------
    count_op = helpers.add_node(other, "SNA_Node_Operator", (-400, 100))
    count_op.socket("label").value = "Print Arranged"
    remote = helpers.add_node(other, "SNA_Node_GetVariable", (-400, -150))
    helpers.point(remote, "var", arranged)
    print_remote = helpers.add_node(other, "SNA_Node_Print", (-100, 100))
    helpers.link(other, count_op.outputs["Execute"], print_remote.inputs[0])
    helpers.link(other, remote.outputs[0], print_remote.inputs[1])
    gone = helpers.add_node(other, "SNA_Node_GlobalVariable", (-400, -350))
    gone.label = "Deleted"
    missing = helpers.add_node(other, "SNA_Node_SetVariable", (-100, -350))
    helpers.point(missing, "var", gone)
    other.nodes.remove(gone)

    for node in tree.nodes:
        node.select = False
    arranged.select = True
    tree.nodes.active = arranged
    helpers.flush()
    return tree


def show(tree):
    window = bpy.context.window_manager.windows[0]
    view = max(window.screen.areas, key=lambda a: a.width * a.height)
    region = next(r for r in view.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=view, region=region):
        bpy.ops.screen.area_split(direction="VERTICAL", factor=0.6)
    views = [a for a in window.screen.areas if a.type == "VIEW_3D"]
    nodes = min(views, key=lambda a: a.x)
    right = max(views, key=lambda a: a.x)
    region = next(r for r in right.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=right, region=region):
        bpy.ops.screen.area_split(direction="HORIZONTAL", factor=0.4)
    views = [a for a in window.screen.areas if a.type == "VIEW_3D" and a != nodes]
    editor = min(views, key=lambda a: a.y)
    view = max(views, key=lambda a: a.y)

    nodes.type = "NODE_EDITOR"
    space = nodes.spaces.active
    space.tree_type = "ScriptingNodeTree"
    space.node_tree = tree
    space.show_region_ui = True
    editor.type = "TEXT_EDITOR"
    editor.spaces.active.text = bpy.data.texts["arrange.py"]
    view.spaces.active.show_region_ui = True
    for area, tab in ((view, "Merge Demo"), (nodes, "Scripting Nodes")):
        for region in area.regions:
            if region.type == "UI":
                try:
                    region.active_panel_category = tab
                except Exception:
                    pass
    return window, nodes


def frame_all(window, area):
    region = next(r for r in area.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.node.view_all()


def start():
    try:
        helpers.enable_addon()
        tree = build()
        window, area = show(tree)
        bpy.app.timers.register(lambda: frame_all(window, area), first_interval=0.5)
        bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
        print("EXAMPLE READY", OUTPUT)
    except Exception:
        traceback.print_exc()
        print("EXAMPLE FAILED")


bpy.app.timers.register(start, first_interval=0.5)
