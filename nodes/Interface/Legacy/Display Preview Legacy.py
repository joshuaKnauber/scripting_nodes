import bpy
from ...base_node import SN_ScriptingBaseNode




class SN_DisplayPreviewNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplayPreviewNode"
    bl_label = "Display Preview (Legacy)"
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_property_input()
        self.add_boolean_input("Show Buttons")
        
    def evaluate(self, context):
        if self.inputs["Property"].is_linked:
            self.code = f"""
                        {self.active_layout}.template_preview({self.inputs['Property'].python_value}, show_buttons={self.inputs['Show Buttons'].python_value})
                        """
        else:
            self.code = f"{self.active_layout}.label(text='No Property connected!', icon='ERROR')"

    def draw_node(self, context, layout):
        box = layout.box()
        box.label(text="Careful! This element is prone to crashes!", icon="INFO")
        box.label(text="Only materials, textures, lights, worlds and line styles can be displayed")