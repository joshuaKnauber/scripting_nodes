import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_BMeshVolumeNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BMeshVolumeNode"
    bl_label = "BMesh Volume"

    def on_create(self, context):
        self.add_execute_input()
        self.add_property_input("BMesh")
        self.add_boolean_input("Signed").default_value = True
        self.add_execute_output()
        self.add_float_output("Volume")

    def evaluate(self, context):
        self.code_import = "import bmesh"
        self.code = f"""
            vol_{self.static_uid} = 0
            if {self.inputs["BMesh"].python_value}:
                vol_{self.static_uid} = {self.inputs["BMesh"].python_value}.calc_volume(signed={self.inputs['Signed'].python_value})
            {self.indent(self.outputs[0].python_value, 3)}
        """
        self.outputs['Volume'].python_value = f"vol_{self.static_uid}"