"""Blender Data nodes: typed outputs, keys, a chain from an input, a property
field with a Blender path."""

import bpy
import helpers


def setup():
    cube = bpy.data.objects.get("Cube")
    if cube is not None:
        cube.modifiers.new("Bevel", "BEVEL")
    tree = helpers.new_tree("Blend Data")
    trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-700, 300))

    active = helpers.add_node(tree, "SNA_Node_BlendData", (-700, 0))
    active.path = "active_object"
    modifiers = helpers.add_node(tree, "SNA_Node_BlendData", (-400, 0))
    modifiers.path_root = "INPUT"
    modifiers.path = "modifiers[]"
    modifiers.path_keys[0].mode = "NAME"
    modifiers.socket("key_0").value = "Bevel"
    helpers.link(tree, active.outputs[0], modifiers.socket("data"))

    data = helpers.add_node(tree, "SNA_Node_BlendData", (-700, -300))
    data.path = "active_object.data"
    data.path_cast = "Mesh"

    fps = helpers.add_node(tree, "SNA_Node_BlendData", (-400, -300))
    fps.paste_path('bpy.data.objects["Cube"].modifiers[0].show_viewport')

    printer = helpers.add_node(tree, "SNA_Node_Print", (-100, 0))
    helpers.link(tree, trigger.outputs[0], printer.inputs[0])
    helpers.link(tree, modifiers.outputs[0], printer.inputs[1])

    panel = helpers.add_node(tree, "SNA_Node_Panel", (-100, -300))
    checkbox = helpers.add_node(tree, "SNA_Node_Checkbox", (200, -300))
    checkbox.mode = "BLENDER"
    checkbox.path = "scene.render.use_simplify"
    helpers.link(tree, panel.outputs["Draw"], checkbox.inputs[0])
    return tree
