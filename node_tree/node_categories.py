from nodeitems_utils import NodeCategory, NodeItem
from .. import auto_load
import os
import inspect



class SN_ScriptingNodesCategory(NodeCategory):
    
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ScriptingNodesTree'



def get_node_categories():
    node_categories = {}

    for cls in auto_load.ordered_classes:
        if cls.bl_rna.base.identifier == "Node":
            category = os.path.basename(os.path.dirname(inspect.getfile(cls)))
            if not category in node_categories: node_categories[category] = []
            node_categories[category].append((cls.bl_label, cls.bl_idname))

    categories = []
    for cat in node_categories:
        names = list(map(lambda node: node[1], sorted(node_categories[cat], key=lambda x: x[0])))
        nodes = list(map(lambda name: NodeItem(name), names))
        categories.append(SN_ScriptingNodesCategory(cat.replace(" ", "_").lower(), cat.replace("_", " "), items=nodes))

    layout_items = [NodeItem("NodeFrame"), NodeItem("NodeReroute")]
    categories.append(SN_ScriptingNodesCategory("LAYOUT", "Layout", items=layout_items))

    return categories