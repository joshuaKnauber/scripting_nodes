#SN_CreateOperator

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python


class SN_CreateOperator(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CreateOperator"
    bl_label = "Create Operator"
    bl_icon = "CONSOLE"
    bl_width_default = 250
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = True

    def update_description(self, context):
        if not is_valid_python(self.description,True):
            self.description = make_valid_python(self.description,True)
    
    def update_op_name(self, context):
        if self.op_name == "":
            self.op_name = "My Operator"
        if not is_valid_python(self.op_name,True):
            self.op_name = make_valid_python(self.op_name,True)

        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname == self.bl_idname:
                if not node == self:
                    if self.op_name == node.op_name:
                        self.op_name = "New " + self.op_name

    op_name: bpy.props.StringProperty(default="My Operator",name="Label",description="Label of the operator", update=update_op_name)
    description: bpy.props.StringProperty(default="My Operators description",name="Description",description="Description of the operator shown in tooltips", update=update_description)
    confirm: bpy.props.BoolProperty(name="Confirm", description="Operator needs to be confirmed")

    def inititialize(self,context):
        self.update_op_name(None)
        self.sockets.create_input(self,"BOOLEAN","Run Condition")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def draw_buttons(self, context, layout):
        layout.prop(self,"op_name")
        layout.prop(self,"description")
        layout.prop(self,"confirm", toggle=True)

    def evaluate(self, socket, node_data, errors):
        execute = ""
        if node_data["output_data"][0]["code"]:
            execute = node_data["output_data"][0]["code"]
        confirm = {"lines": [], "indented": []}
        if self.confirm:
            confirm = {"lines": [], "indented": []}

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
                                [execute],
                                ["return {\"FINISHED\"}"]
                                [""]
                                [""]
                            ]
                        },
                        confirm
                    ]
                }
            ],
            "errors": errors
        }


    def get_register_block(self):
        return ["bpy.utils.register_class(SN_OT_" + self.op_name.replace(" ", "_") + ")"]

    def get_unregister_block(self):
        return ["bpy.utils.unregister_class(SN_OT_" + self.op_name.replace(" ", "_") + ")"]

