import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


class ScriptingNodesTree(bpy.types.NodeTree):
    '''Scripting Nodes node tree'''
    bl_idname = 'ScriptingNodesTree'
    bl_label = "Scripting Nodes"
    bl_icon = 'SCRIPT'


class SN_ScriptingNodesCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ScriptingNodesTree'


node_categories = [

    SN_ScriptingNodesCategory('INTERFACE', "Interface", items=[

        NodeItem("SN_UiPanelNode", settings={
        }),

    ]),

]

def get_node_categories():
    global node_categories
    return node_categories