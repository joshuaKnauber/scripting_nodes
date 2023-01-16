import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IconGalleryNodeNew(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_IconGalleryNodeNew"
    bl_label = "Icon Gallery"
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_property_input("Enum")
        self.add_boolean_input("Show Labels")
        self.add_float_input("Scale").default_value = 5
        self.add_float_input("Scale Popup").default_value = 5
        self.add_interface_output().passthrough_layout_type = True

    def evaluate(self, context):
        if self.inputs["Enum"].is_linked:
            self.code = f"""
                {self.active_layout}.template_icon_view({self.inputs['Enum'].python_source}, '{self.inputs['Enum'].python_attr}', show_labels={self.inputs['Show Labels'].python_value}, scale={self.inputs['Scale'].python_value}, scale_popup={self.inputs['Scale Popup'].python_value})
                {self.indent(self.outputs[0].python_value, 4)}
            """
        else:
            self.code = f"""
                {self.active_layout}.label(text='No Property connected!', icon='ERROR')
                {self.indent(self.outputs[0].python_value, 4)}
            """
