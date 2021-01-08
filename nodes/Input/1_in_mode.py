import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_InModeNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_InModeNode"
    bl_label = "Is In Mode"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    def get_modes(self,context):
        items = []
        modes = ["EDIT_MESH", "EDIT_CURVE", "EDIT_SURFACE", "EDIT_TEXT", "EDIT_ARMATURE",
                "EDIT_METABALL", "EDIT_LATTICE", "POSE", "SCULPT", "PAINT_WEIGHT", "PAINT_VERTEX",
                "PAINT_TEXTURE", "PARTICLE", "OBJECT", "PAINT_GPENCIL", "EDIT_GPENCIL",
                "SCULPT_GPENCIL", "WEIGHT_GPENCIL", "VERTEX_GPENCIL"]
        for mode in modes:
            items.append((mode,mode.replace("_"," ").title(),mode))
        return items

    modes: bpy.props.EnumProperty(items=get_modes,
                                    update=SN_ScriptingBaseNode.auto_compile,
                                    name="Mode",
                                    description="The mode which the active mode is compared to")

    def on_create(self,context):
        self.add_boolean_output("Is In Mode")

    def draw_node(self,context,layout):
        layout.prop(self, "modes", text="")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"\"{self.modes}\"==bpy.context.mode"
        }