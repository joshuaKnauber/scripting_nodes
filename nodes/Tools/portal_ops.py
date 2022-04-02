import bpy
from random import uniform



class SN_OT_ResetPortal(bpy.types.Operator):
    bl_idname = "sn.reset_portal"
    bl_label = "Reset Portal"
    bl_description = "Reset this portal"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        node["var_name"] = node.static_uid
        node.custom_color = (uniform(0,1), uniform(0,1), uniform(0,1))
        return {"FINISHED"}
