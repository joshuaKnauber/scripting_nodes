import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_DisplayPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplayPropertyNode"
    bl_label = "Display Property (Legacy)"
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_property_input()
        self.add_string_input("Label")
        self.add_icon_input("Icon")
        self.add_boolean_input("Emboss").default_value = True
        inp = self.add_boolean_input("Expand")
        inp.default_value = False
        inp.can_be_disabled = True
        inp.disabled = True
        inp = self.add_boolean_input("Slider")
        inp.default_value = False
        inp.can_be_disabled = True
        inp.disabled = True
        inp = self.add_boolean_input("Toggle")
        inp.default_value = False
        inp.can_be_disabled = True
        inp.disabled = True
        inp = self.add_boolean_input("Invert Checkbox")
        inp.default_value = False
        inp.can_be_disabled = True
        inp.disabled = True
        inp = self.add_boolean_input("Full Shortcut")
        inp.default_value = False
        inp.can_be_disabled = True
        inp.disabled = True
        inp = self.add_integer_input("Index")
        inp.can_be_disabled = True
        inp.disabled = True


    def evaluate(self, context):
        if self.inputs["Property"].is_linked:
            attributes = ""
            for inp in self.inputs:
                if inp.can_be_disabled and not inp.disabled:
                    attributes += f", {inp.name.lower().replace(' ', '_')}={inp.python_value}"
            self.code = f"""
                        {self.active_layout}.prop({self.inputs['Property'].python_source}, '{self.inputs['Property'].python_attr.replace("'",'"')}', text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value}, emboss={self.inputs['Emboss'].python_value}{attributes})
                        """
        else:
            self.code = f"""
                        {self.active_layout}.label(text='No Property connected!', icon='ERROR')
                        """