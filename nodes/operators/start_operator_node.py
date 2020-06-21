import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_StartOperator(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_StartOperator"
    bl_label = "Start Operator"
    bl_icon = node_icons["OPERATOR"]
    bl_width_default = 250
    _should_be_registered = True

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def update_name(self, context):
        self.OperatorHandler.set_scene_operators()
        self.socket_update(context)

    opName: bpy.props.StringProperty(name="Name", description="The name of the operator", default="", update=update_name)
    opDescription: bpy.props.StringProperty(name="Description", description="The description of the operator", default="", update=socket_update)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]
        
        self.outputs.new("SN_ProgramSocket", "Program").display_shape = "DIAMOND"
        self.inputs.new("SN_BooleanSocket", "Run Operator").value = True

    def draw_buttons(self, context, layout):
        layout.prop(self,"opName")
        layout.prop(self,"opDescription")

    def free(self):
        self.OperatorHandler.set_scene_operators()
        self.socket_update("context")
    
    def evaluate(self, output):
        execute_code, errors = self.SocketHandler.socket_value(self.outputs[0], False)
        if execute_code == []:
            execute_code = ["pass"]

        name = self.ErrorHandler.handle_text(self.opName)
        poll, error = self.SocketHandler.socket_value(self.inputs[0])
        errors+=error

        return {
            "blocks": [
                {
                    "lines": [
                        ["class SN_OT_" + name + "(bpy.types.Operator):"]
                    ],
                    "indented": [
                        ["bl_idname = \"scripting_nodes." + name.lower() + "\""],
                        ["bl_label = \"" + self.opName +"\""],
                        ["bl_description = \"" + self.opDescription + "\""],
                        ["bl_options = {\"REGISTER\"}"],
                        [""],
                        {
                            "lines": [
                                ["@classmethod"],
                                ["def poll(cls, context):"]
                            ],
                            "indented": [
                                ["return "] + poll
                            ]
                        },
                        [""],
                        {
                            "lines": [
                                ["def execute(self, context):"]
                            ],
                            "indented": [
                                execute_code,
                                ["return {\"FINISHED\"}"]
                            ]
                        }
                    ]
                }
            ],
            "errors": errors
        }

    def get_register_block(self):
        name = self.ErrorHandler.handle_text(self.opName)
        return ["bpy.utils.register_class(SN_OT_" + name + ")"]

    def get_unregister_block(self):
        name = self.ErrorHandler.handle_text(self.opName)
        return ["bpy.utils.unregister_class(SN_OT_" + name + ")"]

    def needed_imports(self):
        return ["bpy"]