#SN_ButtonNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from uuid import uuid4

class SN_ButtonNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ButtonNode"
    bl_label = "Button"
    bl_icon = "RADIOBUT_ON"
    node_color = (0.89,0.6,0)
    should_be_registered = True

    docs = {
        "text": ["The button node creates <important>a clickable button in your layout</>.",
                "",
                "Text Input: <subtext>The text that is displayed on the button</>",
                "Description Input: <subtext>The description of the button</>",
                "Emboss: <subtext>If the input should have an embossed look</>",
                "Depress: <subtext>The button depreesses in the layout</>",
                "Tip: Press CTRL + H to hide unnecessary outputs"],
        "python": ["layout.operator(<string>\"scripting_nodes.my_test_operator\"</>,text=<string>'Test'</>,emboss=True,depress=False)"]

    }

    operator_uid: bpy.props.StringProperty()

    def inititialize(self,context):
        self.operator_uid = uuid4().hex[:10]
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"STRING","Text")
        self.sockets.create_input(self,"STRING","Description")
        self.sockets.create_input(self,"BOOLEAN","Emboss")
        self.sockets.create_input(self,"BOOLEAN","Depress").set_value(False)

        self.sockets.create_output(self,"EXECUTE","Execute")

    def copy(self,context):
        self.operator_uid = uuid4().hex[:10]

    search_value: bpy.props.StringProperty(name="Search value", description="")

    def draw_buttons(self,context,layout):
        self.draw_icon_chooser(layout)

    def evaluate(self, socket, node_data, errors):
        idname = "SNA_OT_BTN_"+self.operator_uid
        icon = ""
        if self.icon:
            icon = ",icon=\""+self.icon+"\""

        if not socket:
            # return the code for the buttons operator
            execute = ""
            if node_data["output_data"][0]["code"]:
                execute = node_data["output_data"][0]["code"]
            return {
                "blocks": [
                    {
                        "lines": [
                            ["class " + idname + "(bpy.types.Operator):"]
                        ],
                        "indented": [
                            ["bl_idname = 'scripting_nodes." + idname.lower() + "'"],
                            ["bl_label = ",node_data["input_data"][1]["code"],""],
                            ["bl_description = ",node_data["input_data"][2]["code"],""],
                            ["bl_options = {\"REGISTER\",\"INTERNAL\"}"],
                            [""],
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
                            }
                        ]
                    }
                ],
                "errors": errors
            }

        else:
            # return the code for the buttons layout
            return {
                "blocks": [
                    {
                        "lines": [
                            [self.inputs[0].links[0].from_node.layout_type(),".operator(\"scripting_nodes.",idname.lower(),
                                        "\",text=",node_data["input_data"][1]["code"],
                                        ",emboss=",node_data["input_data"][3]["code"],
                                        ",depress=",node_data["input_data"][4]["code"],
                                        icon,")"]
                        ],
                        "indented": []
                    }
                ],
                "errors": errors
            }

        return {"blocks": [{"lines": [],"indented": []}], "errors": errors}


    def get_register_block(self):
        return ["bpy.utils.register_class(SNA_OT_BTN_" + self.operator_uid + ")"]

    def get_unregister_block(self):
        return ["bpy.utils.unregister_class(SNA_OT_BTN_" + self.operator_uid + ")"]
