import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_FunctionRunNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for running a function'''
    bl_idname = 'SN_FunctionRunNode'
    bl_label = "Run Function"
    bl_icon = node_icons["OPERATOR"]

    def items_fetch(self, context):
        function_nodes = []
        
        for node in context.space_data.node_tree.nodes:
            if node.bl_idname == "SN_FunctionNode":
                function_nodes.append((str(node.functionName), str(node.functionName), ""))

        return function_nodes

    functionName: bpy.props.EnumProperty(items=items_fetch, name="Name", description="Function Name", default=None, update=None, get=None, set=None)


    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        pIn = self.inputs.new('SN_ProgramSocket', "Program")
        pIn.display_shape = "DIAMOND"

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"functionName",text="Name")

    def evaluate(self,output):
        return {"code": [self.functionName, "()\n"]}