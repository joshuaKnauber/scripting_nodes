import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_GetEditSelectNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_GetEditSelectNode"
    bl_label = "Get Edit Select Mode"
    node_color = "BOOLEAN"

    def on_create(self, context):
        self.add_boolean_output("Vertex")
        self.add_boolean_output("Edge")
        self.add_boolean_output("Face")

    def evaluate(self, context):
        self.outputs[0].python_value = f"bpy.context.tool_settings.mesh_select_mode[0]"
        self.outputs[1].python_value = f"bpy.context.tool_settings.mesh_select_mode[1]"
        self.outputs[2].python_value = f"bpy.context.tool_settings.mesh_select_mode[2]"