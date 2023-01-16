import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_LabelNodeNew(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_LabelNodeNew"
    bl_label = "Label"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label").default_value = "My Label"
        self.add_icon_input("Icon")
        self.add_interface_output().passthrough_layout_type = True

    def evaluate(self, context):
        self.code = f"""
            {self.active_layout}.label(text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value})
            {self.indent(self.outputs[0].python_value, 3)}
        """

    def draw_node(self, context, layout):
        pass