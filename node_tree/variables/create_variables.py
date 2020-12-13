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
        variable.name = "new_variable"
        
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
    
    
    
class SN_OT_AddGetter(bpy.types.Operator):
    bl_idname = "sn.add_getter"
    bl_label = "Add Getter"
    bl_description = "Adds a node which gives you the value of this variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        node = graph_tree.nodes.new("SN_TestNode")
        return {"FINISHED"}
    
    

class SN_OT_AddSetter(bpy.types.Operator):
    bl_idname = "sn.add_setter"
    bl_label = "Add Setter"
    bl_description = "Adds a node which lets you set the value of this variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        node = graph_tree.nodes.new("SN_TestNode")
        return {"FINISHED"}