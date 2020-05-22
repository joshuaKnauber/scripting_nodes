import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ...utitlity_functions import to_lower_camelcase
from ...node_sockets import update_socket_autocompile


class SN_FunctionNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for starting a function'''
    bl_idname = 'SN_FunctionNode'
    bl_label = "Start Function"
    bl_icon = node_icons["OPERATOR"]

    def update_function_name(self,context):
        if not self.updating_props:
            self.updating_props = True
            self.functionName = to_lower_camelcase(self.functionName)
            self.updating_props = False
        update_socket_autocompile(self, context)

    updating_props: bpy.props.BoolProperty(default=False)
    functionName: bpy.props.StringProperty(default="newFunction", update=update_function_name)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        #Node Outputs
        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"functionName",text="Name")
        row = layout.row()
        row.scale_y = 1.5
        row.operator("scripting_nodes.run_function_node",text="Run Function",icon="PLAY").node_name = self.name

    def evaluate(self,output):  
        error = []

        context = bpy.context

        for node in context.space_data.node_tree.nodes:
            if node.bl_idname == "SN_FunctionNode":
                if self.name != node.name:
                    if self.functionName == node.functionName:
                        error.append("same_name_function")

        next_node = None
        if len(self.outputs[0].links) > 0:
            next_node = self.outputs[0].links[0].to_node
        return {
                "code": [],
                "indented_blocks": [
                    {
                        "code": ["def " + self.functionName + "():\n"],
                        "function_node": next_node
                    }
                ],
                "error": error
                }