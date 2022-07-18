import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_DisplayPropertyNodeNew(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplayPropertyNodeNew"
    bl_label = "Display Property"
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
        self.add_interface_output().passthrough_layout_type = True


    def evaluate(self, context):
        if self.inputs["Property"].is_linked:
            attributes = ""
            for inp in self.inputs:
                if inp.can_be_disabled and not inp.disabled:
                    attributes += f", {inp.name.lower().replace(' ', '_')}={inp.python_value}"
            attribute = f"attr_{self.static_uid} = '[\"' + str({self.inputs['Property'].python_attr[1:-1]} + '\"]') " if self.inputs["Property"].python_is_attribute else ""
            self.code = f"""
                            {attribute}
                            {self.active_layout}.prop({self.inputs['Property'].python_source}, {f"attr_{self.static_uid}" if self.inputs["Property"].python_is_attribute else "'" + self.inputs['Property'].python_attr.replace("'", '"') + "'"}, text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value}, emboss={self.inputs['Emboss'].python_value}{attributes})
                            {self.indent(self.outputs[0].python_value, 7)}
                        """
        else:
            self.code = f"""
                            {self.active_layout}.label(text='No Property connected!', icon='ERROR')
                            {self.indent(self.outputs[0].python_value, 7)}
                        """