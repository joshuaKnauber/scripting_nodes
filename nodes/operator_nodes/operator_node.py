import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value
from ...node_sockets import update_socket_autocompile


class SN_OperatorNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to create an operator'''
    bl_idname = 'SN_OperatorNode'
    bl_label = "Operator"
    bl_icon = node_icons["OPERATOR"]
    bl_width_default = 200

    operator_name: bpy.props.StringProperty(default="New Operator",name="Operator name",description="Name of the operator", update=update_socket_autocompile)


    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        self.inputs.new('SN_BooleanSocket', "Should run").value = True

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"operator_name",text="Name")

    def evaluate(self,output):
        errors = []
        pollValue, error = get_input_value(self, "Should run", "SN_BooleanSocket")
        errors+=error

        options = ""

        idname = "SN_OT_" + self.operator_name.title().replace(" ","")
        idname_lower = self.operator_name.lower().replace(" ","_")

        header = ["class " + idname + "(bpy.types.Operator):\n",
                "_INDENT_bl_label = '" + self.operator_name + "'\n",
                "_INDENT_bl_idname = 'sn." + idname_lower + "'\n",
                options,
                "\n_INDENT_@classmethod\n",
                "_INDENT_def poll(self, context):\n",
                "_INDENT__INDENT_return ", pollValue ,"\n\n",
                "_INDENT_def execute(self, context):\n"]

        execute = None
        if self.outputs[0].is_linked:
            execute = self.outputs[0].links[0].to_socket

        functions = [
            {
                "socket": execute,
                "followup": "return {'FINISHED'}\n"
            }
        ]
        
        return {"code":header, "error":errors, "functions":functions}
