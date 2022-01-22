import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyReferenceNode import PropertyReferenceNode



class SN_PropertyNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyReferenceNode):

    bl_idname = "SN_PropertyNode"
    bl_label = "Display Property"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label")
        self.add_icon_input("Icon")

    def evaluate(self, context):
        prop_src = self.get_prop_source()
        if prop_src and self.prop_name and self.prop_name in prop_src.properties:
            if not prop_src.properties[self.prop_name].property_type in ["Group", "Collection"]:
                prop = prop_src.properties[self.prop_name]
                self.code = f"{self.active_layout}.prop(context.scene, '{prop.python_name}', text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value})"

    def draw_node(self, context, layout):
        self.draw_reference_selection(layout)
        prop_src = self.get_prop_source()
        if self.prop_name and prop_src and self.prop_name in prop_src.properties:
            prop = prop_src.properties[self.prop_name]
            if prop.property_type in ["Group", "Collection"]:
                self.draw_warning(layout, "The selected property type can't be displayed!")
            elif prop.property_type == "Pointer" and prop.settings.use_prop_group:
                self.draw_warning(layout, "Can't display pointers with property groups!")