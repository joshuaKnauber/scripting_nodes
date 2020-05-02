import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
from .compile.compiler import ScriptingNodesCompiler


class ScriptingNodesTree(bpy.types.NodeTree):
    '''Scripting Nodes node tree'''
    bl_idname = 'ScriptingNodesTree'
    bl_label = "Scripting Nodes"
    bl_icon = 'SCRIPT'

    def update_info(self,context):
        self.update()

    addon_name: bpy.props.StringProperty(default="New Addon",name="Name",description="Name of your addon",update=update_info)
    addon_author: bpy.props.StringProperty(default="",name="Author",description="Your name",update=update_info)
    addon_description: bpy.props.StringProperty(default="",name="Description",description="Description of what your addon does",update=update_info)
    addon_location: bpy.props.StringProperty(default="",name="Location",description="Location of your addon in blender",update=update_info)
    addon_wiki: bpy.props.StringProperty(default="",name="Wiki",description="Link to the documentation of your addon",update=update_info)
    addon_warning: bpy.props.StringProperty(default="",name="Warning",description="Warning message for your addon",update=update_info)
    addon_category: bpy.props.StringProperty(default="General",name="Category",description="Category of your addon",update=update_info)
    addon_blender: bpy.props.IntVectorProperty(default=bpy.app.version,min=0,name="Version",description="Required blender version for your addon",update=update_info)
    addon_version: bpy.props.IntVectorProperty(default=(1, 0, 0),min=0,name="Version",description="Version of your addon",update=update_info)

    compile_on_start: bpy.props.BoolProperty(default=True,name="Reload on start",description="Reload this node tree when this file is opened")

    compiler = ScriptingNodesCompiler()

    def update(self):
        links_to_remove = []
        
        for link in self.links:
            if link.from_socket.bl_idname == "SN_ProgramSocket" and link.to_socket.bl_idname != "SN_ProgramSocket":
                links_to_remove.append(link)
            elif link.from_socket.bl_idname == "SN_LayoutSocket" and link.to_socket.bl_idname != "SN_LayoutSocket":
                links_to_remove.append(link)
            elif link.from_socket.bl_idname != "SN_LayoutSocket" and link.to_socket.bl_idname == "SN_LayoutSocket":
                links_to_remove.append(link)
            elif link.from_socket.bl_idname != "SN_LayoutSocket" and link.to_socket.bl_idname == "SN_LayoutSocket":
                links_to_remove.append(link)

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
        NodeItem("SN_UiButtonNode", settings={
        }),
        NodeItem("SN_UiLabelNode", settings={
        }),
        NodeItem("SN_UiSeparatorNode", settings={
        }),
        NodeItem("SN_UiRowNode", settings={
        }),
        NodeItem("SN_UiColumnNode", settings={
        }),
        NodeItem("SN_UiSplitNode", settings={
        }),
        NodeItem("SN_UiBoxNode", settings={
        }),
        NodeItem("SN_IfNode", label="If - Layout",settings={
            "is_layout": repr(True),
        }),
        NodeItem("SN_RepeatNode", label="Repeat - Layout", settings={
            "is_layout": repr(True),
        }),

    ]),

    SN_ScriptingNodesCategory('OPERATORS', "Operators", items=[
        
        NodeItem("SN_OperatorNode", settings={
        }),
        NodeItem("SN_PropertiesNode", settings={
        }),
        NodeItem("SN_FunctionNode", settings={
        }),
        NodeItem("SN_FunctionEndNode", settings={
        }),
        NodeItem("SN_FunctionRunNode", settings={
        }),
        NodeItem("SN_VariableSetNode", settings={
        }),
        NodeItem("SN_ScriptLineNode", settings={
        }),

    ]),

    SN_ScriptingNodesCategory('PROGRAM', "Program", items=[
      
        NodeItem("SN_PrintNode", settings={
        }),
        NodeItem("SN_IfNode", label="If - Program", settings={
        }),
        NodeItem("SN_RepeatNode", label="Repeat - Program", settings={
        }),
        NodeItem("SN_VariableChangeNode", settings={
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

        NodeItem("SN_VariableNode", settings={
        }),        
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