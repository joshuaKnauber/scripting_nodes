import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_CreateVariable(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CreateVariable"
    bl_label = "Create Variable"
    bl_icon = node_icons["OPERATOR"]

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    variable_name: bpy.props.StringProperty(name="Name", description="Name of the variable", update=socket_update)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]
        
        inp = self.inputs.new('SN_ProgramSocket', "Program")
        inp.display_shape = "DIAMOND"

        value = self.inputs.new('SN_DataSocket', 'Value')

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

    def draw_buttons(self, context, layout):
        layout.prop(self, "variable_name")

    def evaluate(self, output):
        if self.variable_name != "":
            name = self.ErrorHandler.handle_text(self.variable_name)
        else:
            errors.append({"error": "no_name_var", "node": self})
            name = "placeholder_variable_name"

        value, errors = self.SocketHandler.socket_value(self.inputs[1])
        continue_code, error = self.SocketHandler.socket_value(self.outputs[0], False)
        errors+=error

        return {
            "blocks": [
                {
                    "lines": [
                        [name + " = "] + value
                    ],
                    "indented": [
                    ]
                },
                {
                    "lines": [
                        continue_code
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }

    def needed_imports(self):
        return []