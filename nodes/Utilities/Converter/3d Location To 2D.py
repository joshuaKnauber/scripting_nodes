import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_3DLocationTo2DNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_3DLocationTo2DNode"
    bl_label = "3D View Coordinates To 2D"

    def on_create(self, context):
        self.add_property_input("Area")
        self.add_float_vector_input("Coordinates").size = 3
        self.add_float_vector_output("2D Coordinates")
        
    def evaluate(self, context):
        self.code_import = "from bpy_extras.view3d_utils import location_3d_to_region_2d"
        self.outputs[0].python_value = f"location_3d_to_region_2d({self.inputs[0].python_value}.regions[5], {self.inputs[0].python_value}.spaces[0].region_3d, {self.inputs[1].python_value})"