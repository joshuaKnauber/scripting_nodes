"""Blender Data nodes: the active object, its modifier by name, the mesh
behind it and all materials of the file, read in an operator."""

import bpy
import helpers

WINDOW_SIZE = (1600, 900)


def blend_data(tree, location, path, root="CONTEXT"):
    node = helpers.add_node(tree, "SNA_Node_BlendData", location)
    node.path_root = root
    node.path = path
    return node


def setup():
    cube = bpy.data.objects.get("Cube")
    if cube is not None and "Bevel" not in cube.modifiers:
        cube.modifiers.new("Bevel", "BEVEL")
    tree = helpers.new_tree("Object Report")
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    op = helpers.add_node(tree, "SNA_Node_Operator", (-800, 350))
    op.socket("label").value = "Report"

    active = blend_data(tree, (-800, 50), "active_object")
    bevel = blend_data(tree, (-480, 50), "modifiers[].width", root="INPUT")
    bevel.path_keys[0].mode = "NAME"
    bevel.socket("key_0").value = "Bevel"
    link(active.outputs[0], bevel.socket("data"))
    mesh = blend_data(tree, (-800, -250), "active_object.data")
    mesh.path_cast = "Mesh"
    vertices = blend_data(tree, (-480, -250), "vertices", root="INPUT")
    link(mesh.outputs[0], vertices.socket("data"))
    length = helpers.add_node(tree, "SNA_Node_CollectionLength", (-180, -250))
    link(vertices.outputs[0], length.inputs[0])

    print_width = helpers.add_node(tree, "SNA_Node_Print", (-180, 350))
    print_count = helpers.add_node(tree, "SNA_Node_Print", (100, 350))
    link(op.outputs["Execute"], print_width.inputs[0])
    link(bevel.outputs[0], print_width.inputs[1])
    link(print_width.outputs[0], print_count.inputs[0])
    link(length.outputs[0], print_count.inputs[1])
    helpers.flush()
    return tree
