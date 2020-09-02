#SN_CreateOperator

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_CreateOperator(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CreateOperator"
    bl_label = "Create Operator"
    bl_icon = "CONSOLE"
    bl_width_default = 250
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = True

    op_name: bpy.props.StringProperty(default="My Operator",name="Label",description="Label of the operator")
    description: bpy.props.StringProperty(default="My Operators description",name="Description",description="Description of the operator shown in tooltips")
    confirm: bpy.props.BoolProperty(name="Confirm", description="Operator needs to be confirmed")

    def inititialize(self,context):
        self.sockets.create_input(self,"BOOLEAN","Run Condition")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def draw_buttons(self, context, layout):
        layout.prop(self,"op_name")
        layout.prop(self,"description")
        layout.prop(self,"confirm", toggle=True)

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [
                        ["class SN_OT_" + self.op_name.replace(" ", "_") + "(bpy.types.Operator):"]
                    ],
                    "indented": [
                        ["bl_idname = 'scripting_nodes." + self.op_name.lower().replace(" ", "_") + "'"],
                        ["bl_label = '" + self.op_name +"'"],
                        ["bl_description = '" + self.description + "'"],
                        ["bl_options = {\"REGISTER\"}"],
                        [""],
                        {
                            "lines": [
                                ["@classmethod"],
                                ["def poll(cls, context):"]
                            ],
                            "indented": [
                                ["return ", node_data["input_data"][0]["code"]]
                            ]
                        },
                        [""],
                        {
                            "lines": [
                                ["def execute(self, context):"]
                            ],
                            "indented": [
                                [node_data["output_data"][0]["code"]],
                                ["return {\"FINISHED\"}"]
                            ]
                        }
                    ]
                }
            ],
            "errors": errors
        }


    def get_register_block(self):
        return ["bpy.utils.register_class(SN_OT_" + self.op_name.replace(" ", "_") + ")"]

    def get_unregister_block(self):
        return ["bpy.utils.unregister_class(SN_OT_" + self.op_name.replace(" ", "_") + ")"]
