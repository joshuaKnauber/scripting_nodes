import bpy


class SN_OT_CreateIcon(bpy.types.Operator):
    bl_idname = "sn.add_icon"
    bl_label = "Add Icon"
    bl_description = "Adds a new icon to this addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()

        icon = addon_tree.sn_icons.add()
        icon.name = "NEW_ICON"
        
        addon_tree.sn_icon_index = len(addon_tree.sn_icons)-1
        return {"FINISHED"}



class SN_OT_RemoveIcon(bpy.types.Operator):
    bl_idname = "sn.remove_icon"
    bl_label = "Remove Icon"
    bl_description = "Removes this icon from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        addon_tree = context.scene.sn.addon_tree()
        return len(addon_tree.sn_icons) > 0

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        addon_tree.sn_icons.remove(addon_tree.sn_icon_index)
        if addon_tree.sn_icon_index > 0:
            addon_tree.sn_icon_index -= 1
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)



class SN_OT_AddGetIcon(bpy.types.Operator):
    bl_idname = "sn.add_get_icon"
    bl_label = "Add Getter"
    bl_description = "Adds a node which gives you the name of this icon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        node = graph_tree.nodes.new("SN_TestNode")
        return {"FINISHED"}