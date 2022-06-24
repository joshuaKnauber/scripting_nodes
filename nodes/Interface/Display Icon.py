import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_DisplayIconNodeNew(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplayIconNodeNew"
    bl_label = "Display Icon"
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_icon_input("Icon")
        self.add_float_input("Scale").default_value = 1
        self.add_interface_output().passthrough_layout_type = True

    def evaluate(self, context):
        self.code = f"""
            {self.active_layout}.template_icon(icon_value={self.inputs['Icon'].python_value}, scale={self.inputs['Scale'].python_value})
            {self.indent(self.outputs[0].python_value, 3)}
            """

    def draw_node(self, context, layout):
        layout.label(text="Use this node with care! This might slow down your UI", icon="INFO")