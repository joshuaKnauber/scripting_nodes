import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_EnumSetToListNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_EnumSetToListNode"
    bl_label = "Enum Set To List"

    def on_create(self, context):
        self.add_property_input("Enum Set Property")
        self.add_list_output("List")

    def evaluate(self, context):
        if self.inputs[0].is_linked:
            self.outputs[0].python_value = f"list({self.inputs[0].python_value})"
        else:
            self.outputs[0].reset_value()
