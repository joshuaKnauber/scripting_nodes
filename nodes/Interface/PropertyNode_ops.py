import bpy



class SN_OT_AddNodeProperty(bpy.types.Operator):
    bl_idname = "sn.add_node_property"
    bl_label = "Add Property"
    bl_description = "Adds a property to this node"
    bl_options = {"REGISTER", "INTERNAL"}
    
    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ntree = bpy.data.node_groups[self.node_tree]
        node = ntree.nodes[self.node]
        node.properties.add()
        node.prop_index = len(node.properties) - 1
        return {"FINISHED"}



class SN_OT_RemoveNodeProperty(bpy.types.Operator):
    bl_idname = "sn.remove_node_property"
    bl_label = "Remove Property"
    bl_description = "Removes the selected property from this node"
    bl_options = {"REGISTER", "INTERNAL"}
    
    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ntree = bpy.data.node_groups[self.node_tree]
        node = ntree.nodes[self.node]
        if node.prop_index < len(node.properties):
            node.properties.remove(node.prop_index)
        node.prop_index -= 1
        return {"FINISHED"}



class SN_OT_EditNodeProperty(bpy.types.Operator):
    bl_idname = "sn.edit_node_property"
    bl_label = "Edit Property"
    bl_description = "Opens a popup for editing the selected property"
    bl_options = {"REGISTER", "INTERNAL"}
    
    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        node = bpy.data.node_groups[self.node_tree].nodes[self.node]
        prop = node.properties[node.prop_index]
        prop.draw(context, layout)
        layout.separator()
        prop.settings.draw(context, layout)

    def invoke(self, context, event):
        node = bpy.data.node_groups[self.node_tree].nodes[self.node]
        if node.prop_index < len(node.properties):
            return context.window_manager.invoke_popup(self, width=300)
        return {"FINISHED"}