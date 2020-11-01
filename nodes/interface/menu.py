#SN_MenuNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from uuid import uuid4


class SN_MenuNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_MenuNode"
    bl_label = "Menu"
    bl_icon = "MENU_PANEL"
    bl_width_default = 250
    node_color = (0.89,0.6,0)
    should_be_registered = True

    docs = {
        "text": ["This node adds a <important>menu</>",
                "",
                "Label: <subtext>This is the label that will be shown at the top of the menu.</>",
                "Show Menu: <subtext>This determines if the menu should be shown or hidden.</>",
                "",
                "Menu Output: You can add layouts to the menu here."],
        "python": ["<function>class</> My_MT_Menu(bpy.types.Menu):",
                   "    bl_idname = <string>'My Menu'</>",
                   "    bl_label = <string>'My_MT_Menu'</>",
                   "",
                   "    <yellow>@classmethod</>",
                   "    <grey>def</> <function>poll</>(<blue>cls</>, <blue>context</>):",
                   "        return <red>True</>",
                   "",
                   "    <grey>def</> <function>draw</>(<blue>self</>, <blue>context</>):",
                   "        layout = self.layout",
                   "        pie.<function>label</>(text=<string>\"My label text\"</>, icon=<string>\"MONKEY\"</>)"]
    }

    def update_item(self, context):
        for item in bpy.context.space_data.node_tree.sn_menu_collection_property:
            if item.identifier == self.get_idname():
                item.name = self.label

    label: bpy.props.StringProperty(default="My Menu",name="Label", description="Name shown on the menu", update=update_item)

    menu_uid: bpy.props.StringProperty()

    def inititialize(self,context):
        self.menu_uid = uuid4().hex[:10]
        item = bpy.context.space_data.node_tree.sn_menu_collection_property.add()
        item.identifier = self.get_idname()
        item.name = self.label

        self.sockets.create_input(self,"BOOLEAN","Show Menu")
        self.sockets.create_output(self,"LAYOUT","Menu",True)

    def copy(self,context):
        self.menu_uid = uuid4().hex[:10]
        item = bpy.context.space_data.node_tree.sn_menu_collection_property.add()
        item.identifier = self.get_idname()
        item.name = self.label

    def free(self):
        for x, item in enumerate(bpy.context.space_data.node_tree.sn_menu_collection_property):
            if item.identifier == self.get_idname():
                bpy.context.space_data.node_tree.sn_menu_collection_property.remove(x)

    def draw_buttons(self,context,layout):
        layout.prop(self,"label")

    def layout_type(self):
        return "layout"

    def get_idname(self):
        return "SNA_MT_"+self.menu_uid

    def get_register_block(self):
        return ["bpy.utils.register_class("+self.get_idname()+")"]

    def get_unregister_block(self):
        return ["bpy.utils.unregister_class("+self.get_idname()+")"]

    def evaluate(self, socket, node_data, errors):
        idname = self.get_idname()

        label = self.label
        if label == "":
            label = " "

        menu_layout = []
        for output_data in node_data["output_data"]:
            if output_data["name"] == "Menu" and output_data["code"] != None:
                menu_layout.append([output_data["code"]])
        
        return {
            "blocks": [
                {
                    "lines": [
                        ["class ",idname,"(bpy.types.Menu):"]
                    ],
                    "indented": [
                        ["bl_label = \"",label,"\""],
                        ["bl_idname = \"",idname,"\""],

                        [""],
                        ["@classmethod"],
                        ["def poll(cls, context):"],
                        {
                            "lines": [],
                            "indented": [
                                ["return ",node_data["input_data"][0]["code"]],
                            ]
                        },
                        
                        [""],
                        ["def draw(self, context):"],
                        {
                            "lines": [],
                            "indented": [
                                ["layout = self.layout"],
                            ] + menu_layout
                        },
                        [""],
                        [""],
                    ]
                }
            ],
            "errors": errors
        }
