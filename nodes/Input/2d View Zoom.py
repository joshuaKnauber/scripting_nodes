import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_2DViewZoomNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_2DViewZoomNode"
    bl_label = "2D View Zoom"

    def on_create(self, context):
        self.add_property_input("Area")
        self.add_float_output("Zoom Level")

    def evaluate(self, context):
        self.code_imperative = """
            def get_zoom_level(area):
                for region in area.regions:
                    if region.type == "WINDOW":
                        probe = 1000
                        ui_scale = bpy.context.preferences.system.ui_scale
                        x0, y0 = region.view2d.view_to_region(0, 0, clip=False)
                        x1, y1 = region.view2d.view_to_region(probe * ui_scale, probe * ui_scale, clip=False)
                        return math.sqrt((x1-x0)**2 + (y1-y0)**2) / probe
                return 1
        """
        self.code_import = "import math"
        self.outputs[0].python_value = f"get_zoom_level({self.inputs[0].python_value})"