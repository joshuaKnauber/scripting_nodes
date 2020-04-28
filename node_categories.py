import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


class ScriptingNodesTree(bpy.types.NodeTree):
    '''Scripting Nodes node tree'''
    bl_idname = 'ScriptingNodesTree'
    bl_label = "Scripting Nodes"
    bl_icon = 'SCRIPT'

    addon_name: bpy.props.StringProperty(default="New Addon",name="Name",description="Name of your addon")
    addon_author: bpy.props.StringProperty(default="",name="Author",description="Your name")
    addon_description: bpy.props.StringProperty(default="",name="Description",description="Description of what your addon does")
    addon_location: bpy.props.StringProperty(default="",name="Location",description="Location of your addon in blender")
    addon_warning: bpy.props.StringProperty(default="",name="Warning",description="Warning message for your addon")
    addon_category: bpy.props.StringProperty(default="General",name="Category",description="Category of your addon")
    addon_version: bpy.props.IntVectorProperty(default=(1, 0, 0),min=0,name="Version",description="Version of your addon")


class SN_ScriptingNodesCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ScriptingNodesTree'


node_categories = [

    SN_ScriptingNodesCategory('INTERFACE', "Interface", items=[

        NodeItem("SN_UiPanelNode", settings={
        }),

    ]),
    SN_ScriptingNodesCategory('LOGIC', "Logic", items=[
        
        NodeItem("SN_UiMathNode", settings={
        }),

    ]),

    SN_ScriptingNodesCategory('INPUT', "Input", items=[
        
        NodeItem("SN_NumberNode", settings={
        }),
        NodeItem("SN_BoolNode", settings={
        }),

    ]),

]

def get_node_categories():
    global node_categories
    return node_categories