import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_RegionToViewNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_RegionToViewNode"
    bl_label = "Region To View"

    def on_create(self, context):
        self.add_property_input("Area")
        self.add_float_vector_input("Coordinates").size = 2
        self.add_float_vector_output("View Coordinates")
        
    def evaluate(self, context):
        self.code_imperative = f"""
            def coords_region_to_view(area, coords):
                for region in area.regions:
                    if region.type == "WINDOW":
                        ui_scale = bpy.context.preferences.system.ui_scale
                        x, y = region.view2d.region_to_view(coords[0], coords[1])
                        return (x/ui_scale, y/ui_scale)
                return coords
            """
        self.outputs[0].python_value = f"coords_region_to_view({self.inputs[0].python_value}, tuple({self.inputs[1].python_value}))"