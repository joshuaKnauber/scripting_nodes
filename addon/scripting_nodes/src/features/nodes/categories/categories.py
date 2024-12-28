import inspect
from scripting_nodes import auto_load
from scripting_nodes.src.features.node_tree.node_tree import ScriptingNodeTree
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
import os


class ScriptingNodesCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == ScriptingNodeTree.bl_idname


def get_node_categories():
    class_categories = {}
    for cls in auto_load.ordered_classes:
        if cls.bl_rna.base and cls.bl_rna.base.identifier == "Node":
            path = os.path.dirname(inspect.getfile(cls))
            dirs = path.split(os.sep)
            if not dirs[-1] in class_categories:
                class_categories[dirs[-1]] = []
            class_categories[dirs[-1]].append(cls)

    categories = []
    for category, classes in class_categories.items():
        items = []
        for cls in classes:
            items.append(NodeItem(cls.bl_idname))
        categories.append(ScriptingNodesCategory(category, category, items=items))

    categories.append(
        ScriptingNodesCategory(
            "Layout", "Layout", items=[NodeItem("NodeFrame"), NodeItem("NodeReroute")]
        ),
    )

    return categories


def register():
    get_node_categories()
    nodeitems_utils.register_node_categories("SCRIPTING_NODES", get_node_categories())


def unregister():
    nodeitems_utils.unregister_node_categories("SCRIPTING_NODES")
