#SN_CreateOperator

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python
from uuid import uuid4


class SN_CreateOperator(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CreateOperator"
    bl_label = "Create Operator"
    bl_icon = "SEQ_CHROMA_SCOPE"
    bl_width_default = 250
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = True

    docs = {
        "text": ["Create Operator is used to <important>create an operator</> (duh).",
                "",
                "Label: <subtext>The name of the operator.</>",
                "Description: <subtext>The description of the operator.</>",
                "None/Confirm/Popup: <subtext>Confirm asks you before running the operator.</>",
                "                 <subtext>Popup shows you a popup and runs the operator when clicking OK.</>",
                "Should Run Input: <subtext>Operator isn't executed if False</>"],
        "python": ["<function>class</> My_OT_Operator(bpy.types.Operator):",
                   "    bl_idname = <string>'my_category.my_operator'</>",
                   "    bl_label = <string>'My Operator'</>",
                   "    bl_description = <string>'My Operators description'</>",
                   "    bl_options = {<string>\"REGISTER\"</>,<string>\"UNDO\"</>}",
                   "",
                   "    <yellow>@classmethod</>",
                   "    <grey>def</> <function>poll</>(<blue>cls</>, <blue>context</>):",
                   "        return <red>True</>",
                   "",
                   "    <grey>def</> <function>execute</>(<blue>self</>, <blue>context</>):",
                   "        <function>print</>(<string>\"Hi\"</>)",
                   "        <function>print</>(<string>\"Hello there\"</>)",
                   "        return {<string>\"FINISHED\"</>}",
                   "",
                   "<grey>def</> <function>invoke</>(<blue>self</>, <blue>context</>, <blue>event</>):",
                   "        return context.window_manager.invoke_confirm(self, event)"]

    }


    def update_description(self, context):
        if not is_valid_python(self.description,True):
            self.description = make_valid_python(self.description, True, True)

        for item in bpy.context.space_data.node_tree.custom_operator_properties:
            if item.identifier == self.operator_uid:
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
            if item.identifier == self.operator_uid:
                item.name = self.op_name

        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname in ["SN_RunOperator", "SN_KeymapNode"]:
                node.update_name_external()

    def update_popup(self,context):
        if self.popup_option == "PANEL":
            if len(self.outputs) == 1:
                self.sockets.create_output(self,"LAYOUT","Popup",True)
        else:
            for output in self.outputs:
                if not output == self.outputs[0]:
                    for link in output.links:
                        context.space_data.node_tree.links.remove(link)
            while len(self.outputs) > 1:
                self.sockets.remove_output(self,self.outputs[-1])

    op_name: bpy.props.StringProperty(default="My Operator",name="Label",description="Label of the operator", update=update_op_name)
    description: bpy.props.StringProperty(default="My Operators description",name="Description",description="Description of the operator shown in tooltips", update=update_description)
    popup_option: bpy.props.EnumProperty(name="Popup Type",items=[("NONE","None","None"),("CONFIRM","Confirm","Confirm"),("PANEL","Popup","Popup")],update=update_popup)
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

    def copy(self,context):
        self.operator_uid = uuid4().hex[:10]
        self.update_op_name(None)

        item = bpy.context.space_data.node_tree.custom_operator_properties.add()
        item.name = self.op_name
        item.identifier = self.operator_uid
        item.description = self.description

    def draw_buttons(self, context, layout):
        layout.prop(self,"op_name")
        layout.prop(self,"description")
        row = layout.row()
        row.prop(self,"popup_option", text=" ", expand=True)

    def free(self):
        for x, item in enumerate(bpy.context.space_data.node_tree.custom_operator_properties):
            if item.identifier == self.operator_uid:
                bpy.context.space_data.node_tree.custom_operator_properties.remove(x)

    def layout_type(self):
        return "layout"

    def evaluate(self, socket, node_data, errors):
        execute = "pass"
        if node_data["output_data"][0]["code"]:
            execute = node_data["output_data"][0]["code"]

        popup_text = {"lines": [], "indented": []}
        if self.popup_option == "CONFIRM":
            popup_text = {"lines": [["def invoke(self, context, event):"]], "indented": [["return context.window_manager.invoke_confirm(self, event)"], [""]]}
        elif self.popup_option == "PANEL":
            popup_text = {"lines": [["def invoke(self, context, event):"]], "indented": [["return context.window_manager.invoke_props_dialog(self, width=250)"], [""]]}

        popup_layout = []
        for output_data in node_data["output_data"]:
            if output_data["name"] == "Popup" and output_data["code"] != None:
                popup_layout.append([output_data["code"]])

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
                                {
                                    "lines": [
                                        ["try:"]
                                    ],
                                    "indented": [
                                        ["pass"],
                                        [execute]
                                    ]
                                },
                                {
                                    "lines": [
                                        ["except Exception as exc:"]
                                    ],
                                    "indented": [
                                        ["self.report({\"ERROR\"},message=\"There was an error when running this operation! It has been printed to the console.\")"],
                                        ["print(\"START ERROR | Node Name: ",self.name," | (If you are this addons developer you might want to report this to the Serpens team) \")"],
                                        ["print(\"\")"],
                                        ["print(exc)"],
                                        ["print(\"\")"],
                                        ["print(\"END ERROR - - - - \")"],
                                        ["print(\"\")"]
                                    ]
                                },
                                ["return {\"FINISHED\"}"],
                                [""]
                            ]
                        },
                        {
                            "lines": [
                                ["def draw(self, context):"],
                            ],
                            "indented": [
                                ["layout = self.layout"]
                            ] + popup_layout
                        },
                        popup_text
                    ]
                }
            ],
            "errors": errors
        }


    def get_register_block(self):
        return ["bpy.utils.register_class(SNA_OT_Operator_" + self.operator_uid + ")"]

    def get_unregister_block(self):
        return ["bpy.utils.unregister_class(SNA_OT_Operator_" + self.operator_uid + ")"]

