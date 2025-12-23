import bpy
from ...nodes.compiler import compile_addon



class SN_OT_AddVariable(bpy.types.Operator):
    bl_idname = "sn.add_variable"
    bl_label = "Add Variable"
    bl_description = "Adds a variable to the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ntree = bpy.data.node_groups[self.node_tree]
        new_var = ntree.variables.add()
        new_var.name = new_var.get_unique_name("New Variable")
        ntree.variables.move(len(ntree.variables)-1, ntree.variable_index+1)
        ntree.variable_index += 1
        ntree.variable_index = min(ntree.variable_index, len(ntree.variables)-1)
        return {"FINISHED"}



class SN_OT_RemoveVariable(bpy.types.Operator):
    bl_idname = "sn.remove_variable"
    bl_label = "Remove Variable"
    bl_description = "Removes this variable from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ntree = bpy.data.node_groups[self.node_tree]
        ntree.variables.remove(ntree.variable_index)
        ntree.variable_index -= 1
        compile_addon()
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

    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.scale_y = 1.5
        op = col.operator("sn.add_variable_node", text="Get Variable", icon="ADD")
        op.type = "SN_GetVariableNode"
        op.node_tree = self.node_tree
        op = col.operator("sn.add_variable_node", text="Set Variable", icon="ADD")
        op.type = "SN_SetVariableNode"
        op.node_tree = self.node_tree
        op = col.operator("sn.add_variable_node", text="Reset Variable", icon="ADD")
        op.type = "SN_ResetVariableNode"
        op.node_tree = self.node_tree
        
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)
    
    

class SN_OT_AddVariableNode(bpy.types.Operator):
    bl_idname = "sn.add_variable_node"
    bl_label = "Add Variable Node"
    bl_description = "Adds this node to the editor"
    bl_options = {"REGISTER", "INTERNAL"}

    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    type: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        bpy.ops.node.add_node("INVOKE_DEFAULT", type=self.type, use_transform=True)
        node = context.space_data.node_tree.nodes.active
        ntree = bpy.data.node_groups[self.node_tree]

        if ntree.variable_index < len(ntree.variables):
            var = ntree.variables[ntree.variable_index]
            node.ref_ntree = ntree
            node.var_name = var.name
        return {"FINISHED"}
    
    

class SN_OT_FindVariable(bpy.types.Operator):
    bl_idname = "sn.find_variable"
    bl_label = "Find Variable"
    bl_description = "Finds this variable in the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        ntree = bpy.data.node_groups[self.node_tree]
        
        # init variable nodes
        empty_nodes = []
        variable_nodes = []
        variable = None
        if ntree.variable_index < len(ntree.variables):
            variable = ntree.variables[ntree.variable_index]

        # find variable nodes
        for ngroup in bpy.data.node_groups:
            if ngroup.bl_idname == "ScriptingNodesTree":
                for node in ngroup.nodes:
                    if hasattr(node, "var_name") and hasattr(node, "ref_ntree"):
                        if variable and node.var_name == variable.name and node.ref_ntree == ntree:
                            variable_nodes.append(node)
                        elif not node.var_name or not node.ref_ntree:
                            empty_nodes.append(node)
                        
        # draw nodes for selected variable    
        if ntree.variable_index < len(ntree.variables):
            col = layout.column()
            row = col.row()
            row.enabled = False
            row.label(text=f"Variable: {variable.name}")
            
            for node in variable_nodes:
                op = col.operator("sn.find_node", text=node.name, icon="RESTRICT_SELECT_OFF")
                op.node_tree = node.node_tree.name
                op.node = node.name
            
            if not variable_nodes:
                col.label(text="No nodes found for this variable", icon="INFO")
        
        # draw nodes with empty variable
        col = layout.column()
        row = col.row()
        row.label(text="Empty Variable Nodes")
        row.enabled = False
        
        for node in empty_nodes:
            op = col.operator("sn.find_node", text=node.name, icon="RESTRICT_SELECT_OFF")
            op.node_tree = node.node_tree.name
            op.node = node.name

        if not empty_nodes:
            col.label(text="No empty variable nodes found", icon="INFO")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=250)