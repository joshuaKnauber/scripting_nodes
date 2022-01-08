import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_MakeEnumItemNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_MakeEnumItemNode"
    bl_label = "Make Enum Item"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("Name")
        self.add_string_input("Description")
        self.add_icon_input("Icon")
        self.add_list_output("Item")

    def evaluate(self, context):
        self.outputs[0].python_value = f"[{self.inputs['Name'].python_value}, {self.inputs['Name'].python_value}, {self.inputs['Description'].python_value}, {self.inputs['Icon'].python_value}]"