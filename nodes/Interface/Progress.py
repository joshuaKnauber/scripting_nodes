import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_ProgressNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ProgressNode"
    bl_label = "Progress Indicator"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label").default_value = "My Label"
        self.add_float_input("Factor").default_value = 0.0
        self.add_boolean_input("Ring").default_value = False
        self.add_interface_output().passthrough_layout_type = True

    def evaluate(self, context):
        self.code = f"""
            {self.active_layout}.progress(text={self.inputs['Label'].python_value}, factor={self.inputs['Factor'].python_value}, type='RING' if {self.inputs['Ring'].python_value} else 'BAR')
            {self.indent(self.outputs[0].python_value, 3)}
        """

    def draw_node(self, context, layout):
        pass
