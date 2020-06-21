import bpy
import json


def create_example():

    # # # # # # # # # # # # # # # # # # # #
    NODE_TREE_NAME = "NodeTree"
    EXAMPLE_NAME = ""
    EXAMPLE_ICON = ""
    # # # # # # # # # # # # # # # # # # # #


    nodes = []
    links = []

    for node in bpy.data.node_groups[NODE_TREE_NAME].nodes:
        node_dict = {}
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
                value = input_socket.value
                if type(value) == bpy.types.bpy_prop_array:
                    value = ["v"]
                    for element in input_socket.value:
                        value.append(element)
                input_values.append([index, value])
            except:
                pass
        node_dict["input_values"] = input_values
        nodes.append(node_dict)

    for node in bpy.data.node_groups[NODE_TREE_NAME].nodes:
        for index, out_socket in enumerate(node.outputs):
            if out_socket.is_linked:
                link_dict = {
                    "out_name": node.name,
                    "in_name": out_socket.links[0].to_node.name,
                    "out_index": index,
                    "in_index": 0
                }
                for index, input_socket in enumerate(out_socket.links[0].to_node.inputs):
                    if input_socket == out_socket.links[0].to_socket:
                        link_dict["in_index"] = index
                links.append(link_dict)

    example = {
        "nodes": nodes,
        "links": links,
        "icon": EXAMPLE_ICON
    }


    text = bpy.context.space_data.text
    text.clear()
    text.write("\"" + EXAMPLE_NAME + "\": " + json.dumps(example, indent=4))



def import_example(example,name):
    tree = bpy.data.node_groups.new(name,"ScriptingNodesTree")
    tree.use_fake_user = True
    bpy.context.space_data.node_tree = tree

    for node in example["nodes"]:
        new_node = tree.nodes.new(node["bl_idname"])
        new_node.name = node["name"]
        new_node.location = tuple(node["location"][1:])

        for _ in range(20):
            for prop in node["properties"]:
                try:
                    if type(prop[1]) == list:
                        if prop[1][0] == "v":
                            prop[1] = tuple(prop[1][1:])
                    setattr(new_node,prop[0],prop[1])
                except:
                    pass

        for value in node["input_values"]:
            try:
                if type(value[1]) == list:
                    if value[1][0] == "v":
                        value[1] = tuple(value[1][1:])
                new_node.inputs[value[0]].value = value[1]
            except:
                pass

    for link in example["links"]:
        tree.links.new(tree.nodes[link["in_name"]].inputs[link["in_index"]],tree.nodes[link["out_name"]].outputs[link["out_index"]])