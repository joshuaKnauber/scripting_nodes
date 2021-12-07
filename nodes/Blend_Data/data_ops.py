import bpy



class SN_OT_PasteDataPath(bpy.types.Operator):
    bl_idname = "sn.paste_data_path"
    bl_label = "Paste Data Path"
    bl_description = "Paste the copied data path into this node"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        bpy.data.node_groups[self.node_tree].nodes[self.node].data_path = context.window_manager.clipboard
        return {"FINISHED"}
