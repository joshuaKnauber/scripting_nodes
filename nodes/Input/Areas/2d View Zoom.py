import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_2DViewZoomNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_2DViewZoomNode"
    bl_label = "2D View Zoom"

    def on_create(self, context):
        self.add_property_input("Area")
        self.add_float_output("Zoom Level")

    def evaluate(self, context):
        self.code_imperative = """
            def get_zoom_level(area):
                ui_scale = bpy.context.preferences.system.ui_scale
                for region in area.regions:
                    if region.type == "WINDOW":
                        test_length = 1000
                        x0, y0 = region.view2d.view_to_region(0, 0, clip=False)
                        x1, y1 = region.view2d.view_to_region(test_length, test_length, clip=False)
                        xl = x1 - x0
                        yl = y1 - y0
                        return (math.sqrt(xl**2 + yl**2) / test_length) * ui_scale
                return 1 * ui_scale
        """
        self.code_import = "import math"
        self.outputs[0].python_value = f"get_zoom_level({self.inputs[0].python_value})"