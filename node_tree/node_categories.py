from nodeitems_utils import NodeCategory, NodeItem
from ..utils import get_python_name
from .. import auto_load
import os
import inspect
import bpy



class SN_ScriptingNodesCategory(NodeCategory):
    
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ScriptingNodesTree'



def get_node_categories():
    addon_prefs = bpy.context.preferences.addons[__name__.partition('.')[ 0]].preferences
    node_categories = {}

    for cls in auto_load.ordered_classes:
        if cls.bl_rna.base and cls.bl_rna.base.identifier == "Node":
            category = os.path.basename(os.path.dirname(inspect.getfile(cls)))
            if not category in ["nodes"]:
                if not category in node_categories: node_categories[category] = []
                node_categories[category].append((cls.bl_label, cls.bl_idname))

    layout_items = [("Frame", "NodeFrame"), ("Reroute", "NodeReroute")]
    node_categories["Layout"] = layout_items

    node_categories = dict(sorted(node_categories.items()))

    categories = []
    for cat in node_categories:
        names = list(map(lambda node: node[1], sorted(node_categories[cat], key=lambda x: x[0])))
        nodes = list(map(lambda name: NodeItem(name), names))
        if not cat == "Interface (Legacy)" or addon_prefs.show_legacy_interface:
            categories.append(SN_ScriptingNodesCategory(get_python_name(cat, "category"), cat.replace("_", " "), items=nodes))

    return categories