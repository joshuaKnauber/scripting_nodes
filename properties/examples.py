import bpy
import json
import os


def handle(context, example):
    if not example == "None":
        location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(location, 'examples.json')) as examples:
            examples = json.load(examples)
            example = examples[example]
        
        tree = bpy.data.node_groups.new(example["name"], "ScriptingNodesTree")
        context.space_data.node_tree = tree

        tree.addon_name = example["addon"][0]
        tree.addon_author = example["addon"][1]
        tree.addon_description = example["addon"][2]
        tree.addon_location = example["addon"][3]
        tree.addon_wiki = example["addon"][4]
        tree.addon_warning = example["addon"][5]
        tree.addon_category = example["addon"][6]

        all_nodes = []
        for nodeData in example["nodes"]:
            node = tree.nodes.new(nodeData[0])
            all_nodes.append(node)
            node.location = (nodeData[1], nodeData[2])

        sockets = []
        for node in range(len(example["sockets"])):
            for socket in range(len(example["sockets"][node])):
                if not example["sockets"][node][socket] == []:
                    sockets.append([node, socket, example["sockets"][node][socket][0], example["sockets"][node][socket][1]])

        for node in range(len(example["values"])):
            for attribute in example["values"][node]:
                if example["values"][node][attribute] == "True" or example["values"][node][attribute] == "False":
                    value = eval(example["values"][node][attribute])
                else:
                    value = example["values"][node][attribute]
                all_nodes[node].__setattr__(attribute, value)

        for node in range(len(example["value"])):
            for input_index in example["value"][node]:
                if example["value"][node][str(input_index)] == "True" or example["value"][node][str(input_index)] == "False":
                    all_nodes[node].inputs[eval(input_index)].value = eval(example["value"][node][str(input_index)])
                else:
                    all_nodes[node].inputs[eval(input_index)].value = example["value"][node][str(input_index)]

        for socket in sockets:
            tree.links.new(all_nodes[socket[0]].inputs[socket[1]], all_nodes[socket[2]].outputs[socket[3]])

