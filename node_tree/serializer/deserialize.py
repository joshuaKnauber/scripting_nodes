import bpy
from typing import TypedDict, Tuple, List
import json
import os

class DeserializedNode(TypedDict):
    name: str
    label: str
    idname: str
    location: Tuple[int, int]

class DeserializedNodeTree(TypedDict):
    name: str
    nodes: dict
    index: int
    category: str

class DeserializedAddon(TypedDict):
    trees: dict

def deserialize_addon():
    addon: DeserializedAddon = {
        "trees": {}
    }
    for ntree in bpy.data.node_groups:
        if ntree.bl_idname == "ScriptingNodesTree":
            addon["trees"][ntree.name] = _deserialize_tree(ntree)
    with open(os.path.join(os.path.dirname(bpy.data.filepath), "test", "addon.json"), "w") as file:
        json.dump(addon, file, indent=4)

def _deserialize_tree(ntree) -> DeserializedNodeTree:
    data: DeserializedNodeTree = {
        "name": ntree.name,
        "nodes": {},
        "index": ntree.index,
        "category": ntree.category,
    }
    for node in ntree.nodes:
        data["nodes"][node.static_uid] = _deserialize_node(node)
    return data

def _deserialize_node(node):
    data: DeserializedNode = {
        "name": node.name,
        "idname": node.bl_idname,
        "label": node.label,
        "location": (node.location[0], node.location[1]),
    }
    return data