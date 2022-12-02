import bpy



class SN_OT_AddStringMapItem(bpy.types.Operator):
    bl_idname = "sn.add_string_map_item"
    bl_label = "Add Item"
    bl_description = "Adds an item to this node"
    bl_options = {"REGISTER", "INTERNAL"}

    node_tree: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    node: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    def execute(self, context):
        node = bpy.data.node_groups[self.node_tree].nodes[self.node]
        node.map_collection.add()
        node._evaluate(context)
        return {"FINISHED"}



class SN_OT_RemoveStringMapItem(bpy.types.Operator):
    bl_idname = "sn.remove_string_map_item"
    bl_label = "Remove Item"
    bl_description = "Removes an item from this node"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    node_tree: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    index: bpy.props.IntProperty(options={"HIDDEN", "SKIP_SAVE"})

    def execute(self, context):
        node = bpy.data.node_groups[self.node_tree].nodes[self.node]
        node.map_collection.remove(self.index)
        node._evaluate(context)
        return {"FINISHED"}
