import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_DisplaySearchNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplaySearchNode"
    bl_label = "Display Search"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_collection_property_input("Collection")
        self.add_property_input("String/Pointer")
        self.add_string_input("Label")

    def evaluate(self, context):
        if self.inputs["String/Pointer"].is_linked and self.inputs["Collection"].is_linked:
            self.code = f"{self.active_layout}.prop_search({self.inputs['String/Pointer'].python_value_source}, '{self.inputs['String/Pointer'].python_value_name}', {self.inputs['Collection'].python_value_source}, '{self.inputs['Collection'].python_value_name}', text={self.inputs['Label'].python_value})"
        else:
            self.code = f"{self.active_layout}.label(text='No Property connected!', icon='ERROR')"