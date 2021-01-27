import bpy


class SN_OT_CreateVariable(bpy.types.Operator):
    bl_idname = "sn.add_variable"
    bl_label = "Add Variable"
    bl_description = "Adds a new variable to this graph"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        variable = graph_tree.sn_variables.add()
        variable.node_tree = graph_tree
        variable.name = "New Variable"
        
        graph_tree.sn_variable_index = len(graph_tree.sn_variables)-1
        return {"FINISHED"}



class SN_OT_RemoveVariable(bpy.types.Operator):
    bl_idname = "sn.remove_variable"
    bl_label = "Remove Variable"
    bl_description = "Removes this variable from the graph"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree
        return len(graph_tree.sn_variables) > 0

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree
        graph_tree.sn_variables.remove(graph_tree.sn_variable_index)
        if graph_tree.sn_variable_index > 0:
            graph_tree.sn_variable_index -= 1
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    
class SN_OT_MoveVariable(bpy.types.Operator):
    bl_idname = "sn.move_variable"
    bl_label = "Move Variable"
    bl_description = "Moves this variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    up: bpy.props.BoolProperty()

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree
        
        if (self.up):
            graph_tree.sn_variables.move(graph_tree.sn_variable_index,graph_tree.sn_variable_index-1)
            graph_tree.sn_variable_index -= 1
        else:
            graph_tree.sn_variables.move(graph_tree.sn_variable_index,graph_tree.sn_variable_index+1)
            graph_tree.sn_variable_index += 1
        return {"FINISHED"}

    
class SN_OT_AddVariableGetter(bpy.types.Operator):
    bl_idname = "sn.add_var_getter"
    bl_label = "Add Getter"
    bl_description = "Adds a node which gives you the value of this variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        bpy.ops.node.add_node("INVOKE_DEFAULT",type="SN_GetVariableNode",use_transform=True)
        graph_tree.nodes.active.search_value = graph_tree.sn_variables[graph_tree.sn_variable_index].name
        return {"FINISHED"}


class SN_OT_AddVariableSetter(bpy.types.Operator):
    bl_idname = "sn.add_var_setter"
    bl_label = "Add Setter"
    bl_description = "Adds a node which lets you set the value of this variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    set_type: bpy.props.EnumProperty(items=[("SET","Set","Variable set"),("CHANGE","Change by","Change Variable by")],
                                        options={"SKIP_SAVE"},
                                        name="Setter Type",
                                        description="The setter type for your variable")

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        if self.set_type == "SET":
            bpy.ops.node.add_node("INVOKE_DEFAULT",type="SN_SetVariableNode",use_transform=True)
        else:
            bpy.ops.node.add_node("INVOKE_DEFAULT",type="SN_ChangeVariableNode",use_transform=True)

        graph_tree.nodes.active.search_value = graph_tree.sn_variables[graph_tree.sn_variable_index].name
        return {"FINISHED"}

    def draw(self,context):
        self.layout.prop(self,"set_type",expand=True)

    def invoke(self,context,event):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        if graph_tree.sn_variables[graph_tree.sn_variable_index].var_type in ["STRING", "INTEGER", "FLOAT"]:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)
