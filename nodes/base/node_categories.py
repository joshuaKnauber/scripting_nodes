import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


class SN_ScriptingNodesCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ScriptingNodesTree'


node_categories = [

    SN_ScriptingNodesCategory('INTERFACE', "Interface", items=[
        
    ]),

    SN_ScriptingNodesCategory('FUNCTIONS', "Functions", items=[

    ]),

    SN_ScriptingNodesCategory('PROGRAM', "Program", items=[

    ]),

    SN_ScriptingNodesCategory('VARIABLES', "Variables", items=[
        
    ]),

    SN_ScriptingNodesCategory('LOGIC', "Logic", items=[
        
    ]),
 
    SN_ScriptingNodesCategory('INPUT', "Input", items=[

    ]),

    SN_ScriptingNodesCategory('LAYOUT', "Layout", items=[

        NodeItem("NodeFrame", settings={
        }),
        NodeItem("NodeReroute", settings={
        }),

    ]),

]

def get_node_categories():
    global node_categories
    return node_categories