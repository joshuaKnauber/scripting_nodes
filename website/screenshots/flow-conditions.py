"""A sidebar panel with an If/Else: mesh tools for a mesh, a hint otherwise."""

import bpy
import helpers

WINDOW_SIZE = (1200, 560)
LAYOUT = "split"
SIDEBAR_TAB = "Object Tools"
CROP = (0, 0, 0.855, 0.8)
FRAME = "corner"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Object Tools")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    panel = add("SNA_Node_Panel", -640, 120)
    panel.inputs["Label"].value = "Object Tools"
    obj = add("SNA_Node_BlendData", -720, -110)
    obj.path_root, obj.path = "CONTEXT", "active_object"
    is_mesh = add("SNA_Node_IsObjectType", -430, -110)
    branch = add("SNA_Node_IfElse", -430, 120)
    yes = add("SNA_Node_Label", -220, 200)
    yes.inputs["text"].value = "Mesh tools"
    yes.inputs["icon"].value = "MESH_DATA"
    no = add("SNA_Node_Label", -220, 20)
    no.inputs["text"].value = "Select a mesh first"
    no.inputs["icon"].value = "INFO"
    yes.width = no.width = 210
    helpers.flush()
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    link(panel.outputs["Draw"], branch.inputs[0])
    link(obj.outputs[0], is_mesh.inputs["Object"])
    link(is_mesh.outputs[0], branch.inputs["Condition"])
    link(branch.outputs["Then"], yes.inputs[0])
    link(branch.outputs["Else"], no.inputs[0])
    for node in tree.nodes:
        node.select = False
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
