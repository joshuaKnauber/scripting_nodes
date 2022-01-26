import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyReferenceNode import PropertyReferenceNode



class SN_DisplayPropertyNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyReferenceNode):

    bl_idname = "SN_DisplayPropertyNode"
    bl_label = "Display Property"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_property_input()
        self.add_string_input("Label")
        self.add_icon_input("Icon")

    def evaluate(self, context):
        if self.inputs["Property"].is_linked:
            self.code = f"""
                        prop_src, prop_name = {self.inputs['Property'].python_value}
                        {self.active_layout}.prop(prop_src, prop_name, text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value})
                        """
        else:
            self.code = f"{self.active_layout}.label(text='No Property connected!', icon='ERROR')"
