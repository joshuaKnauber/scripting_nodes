import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyReferenceNode import PropertyReferenceNode



class SN_DisplaySearchNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyReferenceNode):

    bl_idname = "SN_DisplaySearchNode"
    bl_label = "Display Search"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label")
        self.add_collection_property_input()

    def evaluate(self, context):
        prop_src = self.get_prop_source()
        if prop_src and self.prop_name and self.prop_name in prop_src.properties:
            if prop_src.properties[self.prop_name].property_type == "String":
                prop = prop_src.properties[self.prop_name]
                self.code = f"{self.active_layout}.prop_search(context.scene, '{prop.python_name}', bpy.data, 'objects', text={self.inputs['Label'].python_value})"

    def draw_node(self, context, layout):
        self.draw_reference_selection(layout)
        prop_src = self.get_prop_source()
        if self.prop_name and prop_src and self.prop_name in prop_src.properties:
            prop = prop_src.properties[self.prop_name]
            if prop.property_type != "String":
                self.draw_warning(layout, "Please select a string property!")
