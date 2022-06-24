import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_DisplaySearchNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplaySearchNode"
    bl_label = "Display Search (Legacy)"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_collection_property_input("Collection")
        self.add_property_input("String/Pointer")
        self.add_string_input("Label")
        self.add_icon_input("Blender Icon").subtype = "BLENDER_ONLY"

    def evaluate(self, context):
        if len(self.inputs["String/Pointer"].links) and len(self.inputs["Collection"].links):
            self.code = f"""{self.active_layout}.prop_search({self.inputs['String/Pointer'].python_source}, '{self.inputs['String/Pointer'].python_attr.replace("'",'"')}', {self.inputs['Collection'].python_source}, '{self.inputs['Collection'].python_attr.replace("'",'"')}', text={self.inputs['Label'].python_value}, icon={self.inputs['Blender Icon'].python_value})"""
        else:
            self.code = f"{self.active_layout}.label(text='No Property connected!', icon='ERROR')"