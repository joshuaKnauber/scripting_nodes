import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_InModeNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_InModeNode"
    bl_label = "In Mode"
    node_color = "BOOLEAN"

    def get_modes(self,context):
        items = []
        modes = ["EDIT_MESH", "EDIT_CURVE", "EDIT_SURFACE", "EDIT_TEXT", "EDIT_ARMATURE",
                "EDIT_METABALL", "EDIT_LATTICE", "POSE", "SCULPT", "PAINT_WEIGHT", "PAINT_VERTEX",
                "PAINT_TEXTURE", "PARTICLE", "OBJECT", "PAINT_GPENCIL", "EDIT_GPENCIL",
                "SCULPT_GPENCIL" "WEIGHT_GPENCIL", "VERTEX_GPENCIL", "SCULPT_CURVES"]
        for mode in modes:
            items.append((mode,mode.replace("_"," ").title(),mode))
        return items

    modes: bpy.props.EnumProperty(items=get_modes,
                                    update=SN_ScriptingBaseNode._evaluate,
                                    name="Mode",
                                    description="The mode which the active mode is compared to")

    def draw_node(self, context, layout):
        layout.prop(self, "modes", text="")

    def on_create(self, context):
        self.add_boolean_output("In Mode")

    def evaluate(self, context):
        self.outputs[0].python_value = f"'{self.modes}'==bpy.context.mode"