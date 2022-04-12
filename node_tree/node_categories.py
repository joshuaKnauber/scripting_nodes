from nodeitems_utils import NodeCategory, NodeItem
import os
from .. import nodes
import sys
import inspect



class SN_ScriptingNodesCategory(NodeCategory):
    
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ScriptingNodesTree'



def get_node_categories():
    # classes = [obj for name, obj in inspect.getmembers(sys.modules[nodes.__name__], inspect.isclass) if obj.__module__ is nodes.__name__]
    # print(classes)
    

    node_categories_list = {}

    container = os.path.join(os.path.dirname(os.path.dirname(__file__)),"nodes")

    for base, _, files in os.walk(container):
        if not os.path.basename(base) in ["__pycache__","nodes"]:
            if not os.path.basename(base) in node_categories_list:
                node_categories_list[os.path.basename(base)] = []
            for node_file in files:
                if node_file.split(".")[-1] == "py" and not node_file == "__init__.py":
                    node_categories_list[os.path.basename(base)].append(os.path.join(base,node_file))
    
    node_categories = []
    for category in node_categories_list:
        category_items = []
        for node in node_categories_list[category]:
            with open(node, encoding="utf-8") as node_file:
                for line in node_file.readlines():
                    if "class" in line and "SN_ScriptingBaseNode" in line:
                        name = line.split("class ")[-1].split("(")[0]
                        if not name in []:
                            category_items.append(name)
        category_items = list(map(lambda name: NodeItem(name), sorted(category_items)) )
        if category_items:
            node_categories.append(SN_ScriptingNodesCategory(category.replace(" ","_").lower(), category.replace("_", " "), items=category_items))

    layout_items = [NodeItem("NodeFrame"), NodeItem("NodeReroute")]
    node_categories.append(SN_ScriptingNodesCategory("LAYOUT", "Layout", items=layout_items))

    return node_categories