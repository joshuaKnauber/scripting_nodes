import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_NodeGroupOutputNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_NodeGroupOutputNode"
    bl_label = "Group Output"
    bl_width_min = 200

    def on_create(self, context):
        self.add_execute_input()
        self.add_dynamic_data_input("Data")
