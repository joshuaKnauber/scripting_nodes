import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_RunFunction(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunFunction"
    bl_label = "Run Function"
    bl_icon = node_icons["OPERATOR"]

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def items_fetch(self, context):
        function_nodes = []

        if context.space_data != None:
        
            for node in context.space_data.node_tree.nodes:
                if node.bl_idname == "SN_StartFunction":
                    function_identifier = self.ErrorHandler.handle_text(str(node.funcName))
                    function_nodes.append((function_identifier, str(node.funcName), ""))

        return function_nodes

    functionName: bpy.props.EnumProperty(items=items_fetch, name="Name", description="Function Name", update=socket_update)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        self.inputs.new('SN_ProgramSocket', "Program").display_shape = "DIAMOND"

        self.outputs.new('SN_ProgramSocket', "Program").display_shape = "DIAMOND"


    def draw_buttons(self, context, layout):
        layout.prop(self,"functionName",text="Name")

    def evaluate(self, output):
        continue_code, errors = self.SocketHandler.socket_value(self.outputs[0])
        return {
            "blocks": [
                {
                    "lines": [
                        [self.functionName + "()"]
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