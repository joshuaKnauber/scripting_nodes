import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
from .compile.compiler import ScriptingNodesCompiler


class ScriptingNodesTree(bpy.types.NodeTree):
    '''Scripting Nodes node tree'''
    bl_idname = 'ScriptingNodesTree'
    bl_label = "Scripting Nodes"
    bl_icon = 'SCRIPT'

    addon_name: bpy.props.StringProperty(default="New Addon",name="Name",description="Name of your addon")
    addon_author: bpy.props.StringProperty(default="",name="Author",description="Your name")
    addon_description: bpy.props.StringProperty(default="",name="Description",description="Description of what your addon does")
    addon_location: bpy.props.StringProperty(default="",name="Location",description="Location of your addon in blender")
    addon_wiki: bpy.props.StringProperty(default="",name="Wiki",description="Link to the documentation of your addon")
    addon_warning: bpy.props.StringProperty(default="",name="Warning",description="Warning message for your addon")
    addon_category: bpy.props.StringProperty(default="General",name="Category",description="Category of your addon")
    addon_blender: bpy.props.IntVectorProperty(default=bpy.app.version,min=0,name="Version",description="Required blender version for your addon")
    addon_version: bpy.props.IntVectorProperty(default=(1, 0, 0),min=0,name="Version",description="Version of your addon")

    compiler = ScriptingNodesCompiler()

    def update(self):
        links_to_remove = []
        for link in self.links:
            if link.from_socket.bl_idname != link.to_socket.bl_idname:
                pass
                #if not link.from_socket.is_data_socket and link.to_socket.bl_idname == "SN_DataSocket":
                #    links_to_remove.append(link)
            else:
                if link.from_socket.bl_idname == "SN_ProgramSocket" and len(link.from_socket.links) > 1:
                    links_to_remove.append(link.from_socket.links[0])
        for link in links_to_remove:
            self.links.remove(link)
        self.compiler.autocompile()


class SN_ScriptingNodesCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ScriptingNodesTree'


node_categories = [

    SN_ScriptingNodesCategory('INTERFACE', "Interface", items=[

        NodeItem("SN_UiPanelNode", settings={
        }),

    ]),

    SN_ScriptingNodesCategory('OPERATORS', "Operators", items=[
        
        NodeItem("SN_FunctionNode", settings={
        }),
        NodeItem("SN_FunctionEndNode", settings={
        }),

    ]),

    SN_ScriptingNodesCategory('FUNCTIONS', "Functions", items=[
      
        NodeItem("SN_PrintNode", settings={
        }),
        NodeItem("SN_IfNode", settings={
        }),

    ]),

    SN_ScriptingNodesCategory('LOGIC', "Logic", items=[
        
        NodeItem("SN_UiMathNode", settings={
        }),
        NodeItem("SN_CompareNode", settings={
        }),
        NodeItem("SN_AndOrNode", settings={
        }),
        NodeItem("SN_ToStringNode", settings={
        }),

    ]),

    SN_ScriptingNodesCategory('INPUT', "Input", items=[
        
        NodeItem("SN_NumberNode", settings={
        }),
        NodeItem("SN_BoolNode", settings={
        }),
        NodeItem("SN_TextNode", settings={
        }),
        NodeItem("SN_VectorNode", settings={
        }),

    ]),

]

def get_node_categories():
    global node_categories
    return node_categories