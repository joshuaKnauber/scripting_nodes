import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_DisplayEnumItemNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplayEnumItemNode"
    bl_label = "Display Enum Item"
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_property_input()
        self.add_string_input("Item")
        self.add_string_input("Label")
        self.add_interface_output().passthrough_layout_type = True


    def evaluate(self, context):
        if self.inputs["Property"].is_linked and (self.inputs["Item"].is_linked or self.inputs["Item"].default_value):
            self.code = f"""
                        {self.active_layout}.prop_enum({self.inputs['Property'].python_source}, '{self.inputs['Property'].python_attr.replace("'",'"')}', text={self.inputs['Label'].python_value}, value={self.inputs['Item'].python_value})
                        {self.indent(self.outputs[0].python_value, 6)}
                        """
        elif not self.inputs["Property"].is_linked:
            self.code = f"""
                        {self.active_layout}.label(text='No Property connected!', icon='ERROR')
                        {self.indent(self.outputs[0].python_value, 6)}
                        """
        else:
            self.code = f"""
                        {self.active_layout}.label(text='No Enum Item specified!', icon='ERROR')
                        {self.indent(self.outputs[0].python_value, 6)}
                        """