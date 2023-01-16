import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_NoneNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_NoneNode"
    bl_label = "None"

    def on_create(self, context):
        self.add_data_output("None")