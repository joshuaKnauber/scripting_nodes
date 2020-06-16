import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_StartFunction(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_StartFunction"
    bl_label = "Start Function"
    bl_icon = node_icons["SCENE"]
    _should_be_registered = True

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update(context)

    funcName: bpy.props.StringProperty(name="Name", description="The name of the function", default="")

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["PROGRAM"]
        self.outputs.new("SN_ProgramSocket", "Program").display_shape = "DIAMOND"

    def draw_buttons(self, context, layout):
        layout.prop(self,"funcName")

    def evaluate(self, output):
        function_code = ["pass"]
        function_code, errors = self.SocketHandler.socket_value(self.outputs[0], as_list=False)
        if function_code == []:
            function_code = ["pass"]
        if self.funcName != "":
            name = self.ErrorHandler.handle_text(self.funcName)
            name = name.replace(" ", "_")
        else:
            errors.append({"error": "no_name_func", "node": self})
            name = "placeholder_funcName"

        return {
            "blocks": [
                {
                    "lines": [
                        ["def " + name + "():"]
                    ],
                    "indented": [
                        function_code
                    ]
                }
            ],
            "errors": errors
        }

    def needed_imports(self):
        return []


bpy.utils.register_class(SN_StartFunction)