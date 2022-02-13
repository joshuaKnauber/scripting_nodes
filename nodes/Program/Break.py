import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_BreakNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BreakNode"
    bl_label = "Break"
    bl_width_default = 200
    node_color = "PROGRAM"

    def on_create(self, context):
        self.add_execute_input()

    def evaluate(self, context):
        self.code = f"""
                    break
                    """