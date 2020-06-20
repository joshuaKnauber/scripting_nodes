"""

import bpy
import json

# # # # # # # # # # # # # # # # # # # #
NODE_TREE_NAME = "NodeTree"
EXAMPLE_NAME = ""
EXAMPLE_ICON = ""
# # # # # # # # # # # # # # # # # # # #


nodes = []
links = []

for node in bpy.data.node_groups[NODE_TREE_NAME].nodes:
    node_dict = {}
    node_dict["icon"] = EXAMPLE_ICON
    node_dict["bl_idname"] = node.bl_idname
    node_dict["name"] = node.name
    node_dict["location"] = ["v"] + list(node.location)
    properties = []
    for prop in dir(node):
        if not "bl_" in prop and not "__" in prop:
            if type(node.__getattribute__(prop)) in [str, int, float, bool, bpy.types.bpy_prop_array]:
                value = node.__getattribute__(prop)
                if type(value) == bpy.types.bpy_prop_array:
                    value = ["v"]
                    for element in node.__getattribute__(prop):
                        value.append(element)
                properties.append([prop, value])
    node_dict["properties"] = properties
    input_values = []
    for index, input_socket in enumerate(node.inputs):
        try:
            input_values.append([index, input_socket.value])
        except:
            pass
    node_dict["input_values"] = input_values
    nodes.append(node_dict)

for node in bpy.data.node_groups[NODE_TREE_NAME].nodes:
    for index, out_socket in enumerate(node.outputs):
        if out_socket.is_linked:
            link_dict = {
                "in_name": node.name,
                "out_name": out_socket.links[0].to_node.name,
                "in_index": index,
                "out_index": 0
            }
            for index, input_socket in enumerate(out_socket.links[0].to_node.inputs):
                if input_socket == out_socket.links[0].to_socket:
                    link_dict["out_index"] = index
            links.append(link_dict)

example = {
    "nodes": nodes,
    "links": links
}


text = bpy.context.space_data.text
text.clear()
text.write("\"" + EXAMPLE_NAME + "\": " + json.dumps(example, indent=4))

"""