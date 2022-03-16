import bpy



class SN_OT_AddVariable(bpy.types.Operator):
    bl_idname = "sn.add_variable"
    bl_label = "Add Variable"
    bl_description = "Adds a variable to the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ntree = bpy.data.node_groups[self.node_tree]
        new_var = ntree.variables.add()
        new_var.name = "New Variable"
        for index, variable in enumerate(ntree.variables):
            if variable == new_var:
                ntree.variable_index = index
        return {"FINISHED"}



class SN_OT_RemoveVariable(bpy.types.Operator):
    bl_idname = "sn.remove_variable"
    bl_label = "Remove Variable"
    bl_description = "Removes this variable from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ntree = bpy.data.node_groups[self.node_tree]
        # TODO unregister
        ntree.variables.remove(ntree.variable_index)
        ntree.variable_index -= 1
        # TODO register
        return {"FINISHED"}



class SN_OT_MoveVariable(bpy.types.Operator):
    bl_idname = "sn.move_variable"
    bl_label = "Move Variable"
    bl_description = "Moves this variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    move_up: bpy.props.BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ntree = bpy.data.node_groups[self.node_tree]
        if self.move_up:
            ntree.variables.move(ntree.variable_index, ntree.variable_index - 1)
            ntree.variable_index -= 1
        else:
            ntree.variables.move(ntree.variable_index, ntree.variable_index + 1)
            ntree.variable_index += 1
        return {"FINISHED"}



class SN_OT_AddVariableNodePopup(bpy.types.Operator):
    bl_idname = "sn.add_variable_node_popup"
    bl_label = "Add Variable Node Popup"
    bl_description = "Opens a popup to let you choose a variable node"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.scale_y = 1.5
        op = col.operator("sn.add_variable_node", text="Get Variable", icon="ADD")
        op.type = "SN_GetVariableNode"
        op = col.operator("sn.add_variable_node", text="Set Variable", icon="ADD")
        op.type = "SN_SetVariableNode"
        op = col.operator("sn.add_variable_node", text="Reset Variable", icon="ADD")
        op.type = "SN_ResetVariableNode"
        
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)
    
    

class SN_OT_AddVariableNode(bpy.types.Operator):
    bl_idname = "sn.add_variable_node"
    bl_label = "Add Variable Node"
    bl_description = "Adds this node to the editor"
    bl_options = {"REGISTER", "INTERNAL"}

    type: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        bpy.ops.node.add_node("INVOKE_DEFAULT", type=self.type, use_transform=True)
        node = context.space_data.node_tree.nodes.active

        if context.space_data.node_tree.variable_index < len(context.space_data.node_tree.variables):
            var = context.space_data.node_tree.variables[context.space_data.node_tree.variable_index]
            node.var_ntree = context.space_data.node_tree
            node.var_name = var.name
        return {"FINISHED"}