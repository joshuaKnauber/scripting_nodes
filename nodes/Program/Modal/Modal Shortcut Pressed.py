import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ModalShortcutPressedNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_ModalShortcutPressedNode"
    bl_label = "Modal Shortcut Pressed"
    node_color = "DEFAULT"

    def on_create(self, context):
        items = bpy.types.Event.bl_rna.properties["type"].enum_items
        self.add_enum_input("Type")["items"] = str([item.identifier for item in items])
        self.add_boolean_input("Alt")
        self.add_boolean_input("Shift")
        self.add_boolean_input("Ctrl")
        self.add_boolean_input("Os Key")
        self.add_boolean_output("Shortcut Pressed")

    def evaluate(self, context):
        self.outputs[0].python_value = f"(event.type == {self.inputs['Type'].python_value} and event.value == 'PRESS' and event.alt == {self.inputs['Alt'].python_value} and event.shift == {self.inputs['Shift'].python_value} and event.ctrl == {self.inputs['Ctrl'].python_value})"