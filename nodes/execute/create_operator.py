#SN_CreateOperator

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python
from uuid import uuid4


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
        
        for item in bpy.context.space_data.node_tree.custom_operator_properties:
            if item.name == self.group_item:
                self.group_item = self.description
                item.description = self.description
    
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

        for item in bpy.context.space_data.node_tree.custom_operator_properties:
            if item.name == self.group_item:
                self.group_item = self.op_name
                item.name = self.op_name

    op_name: bpy.props.StringProperty(default="My Operator",name="Label",description="Label of the operator", update=update_op_name)
    description: bpy.props.StringProperty(default="My Operators description",name="Description",description="Description of the operator shown in tooltips", update=update_description)
    confirm_option: bpy.props.BoolProperty(name="Confirm", description="Operator needs to be confirmed")
    group_item: bpy.props.StringProperty()
    operator_uid: bpy.props.StringProperty()

    def inititialize(self,context):
        self.operator_uid = uuid4().hex[:10]
        self.update_op_name(None)
        self.sockets.create_input(self,"BOOLEAN","Should Run")
        self.sockets.create_output(self,"EXECUTE","Execute")
        item = bpy.context.space_data.node_tree.custom_operator_properties.add()
        item.name = self.op_name
        item.identifier = self.operator_uid
        item.description = self.description
        self.group_item = item.name

    def draw_buttons(self, context, layout):
        layout.prop(self,"op_name")
        layout.prop(self,"description")
        layout.prop(self,"confirm_option", toggle=True)

    def free(self):
        for x, item in enumerate(bpy.context.space_data.node_tree.custom_operator_properties):
            if item.name == self.group_item:
                bpy.context.space_data.node_tree.custom_operator_properties.remove(x)

    def evaluate(self, socket, node_data, errors):
        execute = ""
        if node_data["output_data"][0]["code"]:
            execute = node_data["output_data"][0]["code"]
        confirm_text = {"lines": [], "indented": []}
        if self.confirm_option:
            confirm_text = {"lines": [["def invoke(self, context, event):"]], "indented": [["return context.window_manager.invoke_confirm(self, event)"], [""]]}

        return {
            "blocks": [
                {
                    "lines": [
                        ["class SNA_OT_Operator_" + self.operator_uid + "(bpy.types.Operator):"]
                    ],
                    "indented": [
                        ["bl_idname = 'scripting_nodes.sna_ot_operator_" + self.operator_uid.lower() + "'"],
                        ["bl_label = '" + self.op_name +"'"],
                        ["bl_description = '" + self.description + "'"],
                        ["bl_options = {\"REGISTER\",\"UNDO\"}"],
                        [""],
                        {
                            "lines": [
                                ["@classmethod"],
                                ["def poll(cls, context):"]
                            ],
                            "indented": [
                                ["return ", node_data["input_data"][0]["code"]],
                                [""],
                            ],
                        },
                        {
                            "lines": [
                                ["def execute(self, context):"]
                            ],
                            "indented": [
                                [execute],
                                ["return {\"FINISHED\"}"],
                                [""]
                            ]
                        },
                        confirm_text
                    ]
                }
            ],
            "errors": errors
        }


    def get_register_block(self):
        return ["bpy.utils.register_class(SNA_OT_Operator_" + self.operator_uid + ")"]

    def get_unregister_block(self):
        return ["bpy.utils.unregister_class(SNA_OT_Operator_" + self.operator_uid + ")"]

