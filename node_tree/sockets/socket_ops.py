import bpy



class SN_AddDynamic(bpy.types.Operator):
    bl_idname = "sn.add_dynamic"
    bl_label = "Add Dynamic Socket"
    bl_description = "Add another socket like this one"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    is_output: bpy.props.BoolProperty(options={"HIDDEN", "SKIP_SAVE"})
    index: bpy.props.IntProperty(options={"HIDDEN", "SKIP_SAVE"})
    insert_above: bpy.props.BoolProperty(default=False, options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data, "node_tree") and context.space_data.node_tree

    def execute(self, context):
        # find node in node tree
        ntree = context.space_data.node_tree
        if self.node in ntree.nodes:
            node = ntree.nodes[self.node]

            # find socket
            if self.is_output:
                socket = node.outputs[self.index]
            else:
                socket = node.inputs[self.index]
                
            # trigger adding dynamic socket
            socket.trigger_dynamic(self.insert_above)

            # trigger reevaluation
            node.evaluate(context)
        return {"FINISHED"}



class SN_RemoveSocket(bpy.types.Operator):
    bl_idname = "sn.remove_socket"
    bl_label = "Remove Socket"
    bl_description = "Removes this socket"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    is_output: bpy.props.BoolProperty(options={"HIDDEN", "SKIP_SAVE"})
    index: bpy.props.IntProperty(options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data, "node_tree") and context.space_data.node_tree

    def execute(self, context):
        # find node in node tree
        ntree = context.space_data.node_tree
        if self.node in ntree.nodes:
            node = ntree.nodes[self.node]

            # find socket
            if self.is_output:
                node.outputs.remove(node.outputs[self.index])
            else:
                node.inputs.remove(node.inputs[self.index])

            # trigger reevaluation
            node.evaluate(context)
        return {"FINISHED"}
