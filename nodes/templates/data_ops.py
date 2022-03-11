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

            # paste in blender property
            if node.bl_idname == "SN_BlenderPropertyNode":
                node.pasted_data_path = context.window_manager.clipboard
                # can set data type
                if context.window_manager.clipboard == context.scene.sn.last_copied_datapath and \
                    context.scene.sn.last_copied_datatype in node.socket_names:
                    node.outputs["Value"].data_type = node.socket_names[context.scene.sn.last_copied_datatype]
                # data type is function
                elif "(" in  context.window_manager.clipboard and ")" in context.window_manager.clipboard:
                    loc = node.location
                    ntree = node.node_tree
                    ntree.nodes.remove(node)
                    node = ntree.nodes.new("SN_RunPropertyFunctionNode")
                    node.location = loc
                    node.pasted_data_path = context.window_manager.clipboard
                # can't set data type
                else:
                    node.outputs["Value"].data_type = node.socket_names["Data"]
                    self.report({"WARNING"}, message="Couldn't set the output value data type!")
            
            # paste in run property function
            elif node.bl_idname == "SN_RunPropertyFunctionNode":
                # is function
                if "(" in  context.window_manager.clipboard and ")" in context.window_manager.clipboard:
                    node.pasted_data_path = context.window_manager.clipboard
                # isn't function
                else:
                    self.report({"ERROR"}, message="Can only paste functions in this node!")
        else:
            self.report({"ERROR"}, message="Not a valid blender data path. Use the blend data browser.")
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
