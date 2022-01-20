import bpy
from ..base_node import SN_ScriptingBaseNode




class SN_DisplayPreviewNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplayPreviewNode"
    bl_label = "Display Preview"
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_blend_data_input("Blend Data")
        self.add_boolean_input("Show Buttons")
        
    supported_types: bpy.props.BoolProperty(name="Supported Types",
                                    description="Supported types are Material, Texture, Light, World or Line Style. Show Buttons doesn't work for all types",
                                    get=lambda self: False,
                                    set=lambda self, value: None)

    def evaluate(self, context):
        self.code = f"""
            if {self.inputs['Blend Data'].python_value}:
                {self.active_layout}.template_preview({self.inputs['Blend Data'].python_value}, show_buttons={self.inputs['Show Buttons'].python_value})
            """

    def draw_node(self, context, layout):
        layout.prop(self, "supported_types", text="Supported Types", toggle=True, emboss=False, icon="INFO")