import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IsExportNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IsExportNode"
    bl_label = "Is Export"
    node_color = "BOOLEAN"

    def on_create(self, context):
        self.add_boolean_output("Is Export")

    def evaluate(self, context):
        self.outputs[0].python_value = f"False"

    def evaluate_export(self, context):
        self.outputs[0].python_value = f"True"