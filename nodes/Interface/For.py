import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ForInterfaceNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ForInterfaceNode"
    bl_label = "For Interface"
    bl_width_default = 200
    node_color = "INTERFACE"
    layout_type = "layout"
    
    def on_create(self, context):
        self.add_interface_input()
        self.add_collection_property_input("Collection")
        self.add_interface_output("Repeat")
        self.add_interface_output("Continue")
        self.add_property_output("Property")
        self.add_integer_output("Index")
        
    def on_link_insert(self, from_socket, to_socket, is_output):
        if to_socket == self.inputs[0]:
            self.layout_type = self.active_layout

    def evaluate(self, context):
        if self.inputs["Collection"].is_linked:
            self.outputs["Index"].python_value = f"i_{self.static_uid}"
            self.outputs["Property"].python_value = f"{self.inputs['Collection'].python_value}[i_{self.static_uid}]"
            self.code = f"""
                        for i_{self.static_uid} in range(len({self.inputs['Collection'].python_value})):
                            {self.indent(self.outputs['Repeat'].python_value, 7) if self.outputs['Repeat'].python_value.strip() else 'pass'}
                        {self.indent(self.outputs['Continue'].python_value, 6)}
                        """
        else:
            self.code = f"""
                        {self.active_layout}.label(text='No Collection property connected!', icon='ERROR')
                        {self.indent(self.outputs['Continue'].python_value, 6)}
                        """
            self.outputs["Index"].reset_value()
            self.outputs["Property"].reset_value()