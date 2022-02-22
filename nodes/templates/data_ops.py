import bpy



class SN_OT_PasteDataPath(bpy.types.Operator):
    bl_idname = "sn.paste_data_path"
    bl_label = "Paste Data Path"
    bl_description = "Paste the copied data path into this node"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        if "bpy." in context.window_manager.clipboard:
            node = bpy.data.node_groups[self.node_tree].nodes[self.node]
            node.pasted_data_path = context.window_manager.clipboard
            if "Value" in node.outputs and context.scene.sn.last_copied_datapath == context.window_manager.clipboard:
                node.outputs["Value"].data_type = node.socket_names[context.scene.sn.last_copied_datatype]
        else:
            self.report({"ERROR"}, message="Not a valid blender data path. Use the Rightclick Menu -> Get Serpens Property button")
        return {"FINISHED"}



class SN_OT_ResetDataPath(bpy.types.Operator):
    bl_idname = "sn.reset_data_path"
    bl_label = "Reset Data Path"
    bl_description = "Resets the data path of this node"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        bpy.data.node_groups[self.node_tree].nodes[self.node].pasted_data_path = ""
        return {"FINISHED"}
