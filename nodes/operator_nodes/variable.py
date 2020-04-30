import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ...node_sockets import update_socket_autocompile


class SN_VariableSetNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for setting a variable'''
    bl_idname = 'SN_VariableSetNode'
    bl_label = "Create Variable"
    bl_icon = node_icons["OPERATOR"]

    variable_name: bpy.props.StringProperty(name="Name", description="Name of the variable", update=update_socket_autocompile)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        pIn = self.inputs.new('SN_ProgramSocket', "Program")
        pIn.display_shape = "DIAMOND"

        value = self.inputs.new('SN_DataSocket', 'Value')

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self, "variable_name")

    def evaluate(self,output):
        errors = []

        if self.variable_name == "":
            errors.append("no_name")

        if not self.inputs[1].is_linked:
            errors.append("no_connection")
            return {"code": [self.variable_name, " = ", "0", "\n"], "error": errors}

        return {"code": [self.variable_name, " = ", self.inputs[1].links[0].from_socket, "\n"], "error": errors}
