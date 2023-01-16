import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_SeparatorNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_SeparatorNode"
    bl_label = "Separator (Legacy)"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_float_input("Factor").default_value = 1.0

    def evaluate(self, context):
        self.code = f"""
            {self.active_layout}.separator(factor={self.inputs['Factor'].python_value})
        """
