import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyReferenceNode import PropertyReferenceNode



class SN_DisplayPropertyNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyReferenceNode):

    bl_idname = "SN_DisplayPropertyNode"
    bl_label = "Display Property"
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_property_input()
        self.add_string_input("Label")
        self.add_icon_input("Icon")
        self.add_boolean_input("Emboss").default_value = True
        self.add_boolean_input("Expand").default_value = False
        self.add_boolean_input("Slider").default_value = False
        self.add_boolean_input("Toggle").default_value = False
        self.add_boolean_input("Invert Checkbox").default_value = False


    def evaluate(self, context):
        if self.inputs["Property"].is_linked:
            self.code = f"""
                        {self.active_layout}.prop({self.inputs['Property'].python_source}, '{self.inputs['Property'].python_attr}', text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value}, emboss={self.inputs['Emboss'].python_value}, expand={self.inputs['Expand'].python_value}, slider={self.inputs['Slider'].python_value}, toggle={self.inputs['Toggle'].python_value}, invert_checkbox={self.inputs['Invert Checkbox'].python_value})
                        """
        else:
            self.code = f"""
                        {self.active_layout}.label(text='No Property connected!', icon='ERROR')
                        """