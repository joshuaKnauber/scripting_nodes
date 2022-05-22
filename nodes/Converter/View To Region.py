import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ViewToRegionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ViewToRegionNode"
    bl_label = "View To Region"

    def on_create(self, context):
        self.add_property_input("Area")
        self.add_float_vector_input("Coordinates").size = 2
        self.add_float_vector_output("Region Coordinates")
        
    def evaluate(self, context):
        self.code_imperative = f"""
            def coords_view_to_region(area, coords):
                for region in area.regions:
                    if region.type == "WINDOW":
                        ui_scale = bpy.context.preferences.system.ui_scale
                        return region.view2d.view_to_region(coords[0]*ui_scale, coords[1]*ui_scale, clip=False)
                return coords
            """
        self.outputs[0].python_value = f"coords_view_to_region({self.inputs[0].python_value}, tuple({self.inputs[1].python_value}))"