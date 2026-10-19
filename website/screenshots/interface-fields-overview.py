"""A sidebar panel with one field of each kind (Checkbox, Number Field
with Slider, Vector Field, Text Field, expanded Enum Menu and a Pointer
Field drawing Blender's material selector), next to the node tree."""

import bpy
import helpers

WINDOW_SIZE = (1250, 700)
LAYOUT = "split"
SIDEBAR_TAB = "Scatter"
CROP = (0, 0, 0.835, 0.74)
FRAME = "corner"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Scatter Tools"
    # ids: adding to a list can move earlier items (helpers.prop)
    smooth = helpers.add_property("Smooth", "BOOLEAN", default_bool=True).id
    strength = helpers.add_property(
        "Strength", "FLOAT", default_float=0.6, use_min=True, use_max=True
    ).id
    offset = helpers.add_property("Offset", "VECTOR").id
    prefix = helpers.add_property("Prefix", "STRING").id
    mode = helpers.add_property("Mode", "ENUM")
    mode.enum_items[0].name = "Random"
    mode.enum_items[1].name = "Grid"
    mode = mode.id

    tree = helpers.new_tree("Scatter Panel")
    panel = helpers.add_node(tree, "SNA_Node_Panel", (-720, 100))
    panel.inputs["Label"].value = "Scatter"
    panel.panel_category = "Scatter"

    def field(idname, prop, location, **settings):
        node = helpers.add_node(tree, idname, location)
        if prop:
            helpers.pick_property(node, helpers.prop(prop))
        for name, value in settings.items():
            setattr(node, name, value)
        return node

    nodes = [
        field("SNA_Node_EnumMenu", mode, (-480, 200), expand=True),
        field("SNA_Node_Checkbox", smooth, (-240, 200)),
        field("SNA_Node_NumberField", strength, (0, 200), slider=True),
        field("SNA_Node_VectorField", offset, (-480, -120)),
        field("SNA_Node_TextField", prefix, (-240, -120)),
        field(
            "SNA_Node_PointerField",
            None,
            (0, -120),
            mode="BLENDER",
            path="object.active_material",
            style="SELECTOR",
        ),
    ]
    nodes[4].socket("placeholder").value = "Name prefix"
    nodes[5].socket("new").value = "material.new"
    previous = panel.outputs["body"]
    for node in nodes:
        helpers.link(tree, previous, node.inputs[0])
        previous = node.outputs[0]
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
