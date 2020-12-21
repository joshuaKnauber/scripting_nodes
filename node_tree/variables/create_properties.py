import bpy


class SN_OT_CreateProperty(bpy.types.Operator):
    bl_idname = "sn.add_property"
    bl_label = "Add Property"
    bl_description = "Adds a new property to this addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()

        variable = addon_tree.sn_properties.add()
        variable.is_property = True
        variable.node_tree = addon_tree
        variable.name = "new_property"
        
        addon_tree.sn_property_index = len(addon_tree.sn_properties)-1
        return {"FINISHED"}



class SN_OT_RemoveProperty(bpy.types.Operator):
    bl_idname = "sn.remove_property"
    bl_label = "Remove Property"
    bl_description = "Removes this property from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        addon_tree = context.scene.sn.addon_tree()
        return len(addon_tree.sn_properties) > 0

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        addon_tree.sn_properties.remove(addon_tree.sn_property_index)
        if addon_tree.sn_property_index > 0:
            addon_tree.sn_property_index -= 1
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    
    
class SN_OT_AddPropertyGetter(bpy.types.Operator):
    bl_idname = "sn.add_prop_getter"
    bl_label = "Add Getter"
    bl_description = "Adds a node which gives you the value of this variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        node = graph_tree.nodes.new("SN_TestNode")
        return {"FINISHED"}
    
    

class SN_OT_AddPropertySetter(bpy.types.Operator):
    bl_idname = "sn.add_prop_setter"
    bl_label = "Add Setter"
    bl_description = "Adds a node which lets you set the value of this variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        node = graph_tree.nodes.new("SN_TestNode")
        return {"FINISHED"}