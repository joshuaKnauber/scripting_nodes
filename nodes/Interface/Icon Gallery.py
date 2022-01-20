import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyReferenceNode import PropertyReferenceNode



class SN_IconGalleryNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyReferenceNode):

    bl_idname = "SN_IconGalleryNode"
    bl_label = "Icon Gallery"
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_boolean_input("Show Labels")
        self.add_float_input("Scale").default_value = 5
        self.add_float_input("Scale Popup").default_value = 5
        self.add_blend_data_input("Blend Data") # TODO

    def evaluate(self, context):
        enum_src = self.get_prop_source()
        if enum_src and self.prop_name in enum_src.properties and enum_src.properties[self.prop_name].property_type == "Enum":
            prop = enum_src.properties[self.prop_name]
            self.code = f"{self.active_layout}.template_icon_view(context.scene, '{prop.python_name}', show_labels={self.inputs['Show Labels'].python_value}, scale={self.inputs['Scale'].python_value}, scale_popup={self.inputs['Scale Popup'].python_value})"

    def draw_node(self, context, layout):
        self.draw_reference_selection(layout)
        prop_src = self.get_prop_source()
        if self.prop_name and prop_src and self.prop_name in prop_src.properties:
            if prop_src.properties[self.prop_name].property_type != "Enum":
                self.draw_warning(layout, "The selected property is not an enum property!")
            elif not prop_src.properties[self.prop_name].settings.is_dynamic:
                self.draw_warning(layout, "The selected property does not have dynamic items!")