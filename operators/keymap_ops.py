import bpy

class SN_AddKeymapItem(bpy.types.Operator):
    bl_idname = "scripting_nodes.add_keymap_item"
    bl_label = "Add Keymap Item"
    bl_description = "Adds a keymap item to this keymap"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    node_name: bpy.props.StringProperty()

    def execute(self, context):
        context.space_data.node_tree.nodes[self.node_name].keymap_items.add()
        return {"FINISHED"}

class SN_RemoveKeymapItem(bpy.types.Operator):
    bl_idname = "scripting_nodes.remove_keymap_item"
    bl_label = "Remove Keymap Item"
    bl_description = "Removes a keymap item to this keymap"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    index: bpy.props.IntProperty()
    node_name: bpy.props.StringProperty()

    def execute(self, context):
        context.space_data.node_tree.nodes[self.node_name].keymap_items.remove(self.index)
        return {"FINISHED"}
