import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ForExecuteNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ForExecuteNode"
    bl_label = "For Execute"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_collection_property_input("Collection")
        self.add_execute_output("Repeat")
        self.add_execute_output("Continue")
        self.add_property_output("Property")
        self.add_integer_output("Index")

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
            self.code = f"""print("No Collection property connected to {self.name}!")"""
            self.outputs["Index"].reset_value()
            self.outputs["Property"].reset_value()