import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_PrintNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_PrintNode"
    bl_label = "Print"

    def on_create(self, context):
        self.add_execute_input()
        self.add_string_input()
        self.add_data_input()
        self.add_execute_output()
