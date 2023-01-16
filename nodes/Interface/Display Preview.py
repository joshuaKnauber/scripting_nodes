import bpy
from ..base_node import SN_ScriptingBaseNode




class SN_DisplayPreviewNodeNew(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_DisplayPreviewNodeNew"
    bl_label = "Display Preview"
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_property_input()
        self.add_boolean_input("Show Buttons")
        self.add_interface_output().passthrough_layout_type = True
        
    def evaluate(self, context):
        if self.inputs["Property"].is_linked:
            self.code = f"""
                        {self.active_layout}.template_preview({self.inputs['Property'].python_value}, show_buttons={self.inputs['Show Buttons'].python_value})
                        {self.indent(self.outputs[0].python_value, 6)}
                        """
        else:
            self.code = f"""
                {self.active_layout}.label(text='No Property connected!', icon='ERROR')
                {self.indent(self.outputs[0].python_value, 4)}
                """

    def draw_node(self, context, layout):
        box = layout.box()
        box.label(text="Careful! This element is prone to crashes!", icon="INFO")
        box.label(text="Only materials, textures, lights, worlds and line styles can be displayed")