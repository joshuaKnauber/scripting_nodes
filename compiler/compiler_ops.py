import bpy
from .compiler import compile_addon, remove_addon, addon_is_registered



class SN_OT_Compile(bpy.types.Operator):
    bl_idname = "sn.compile"
    bl_label = "Compile"
    bl_description = "Compiles all graphs with changes"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    @classmethod
    def poll(cls, context):
        return context.scene.sn.addon_tree() != None

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        
        success = compile_addon(addon_tree)
        
        if success:
            self.report({"INFO"},message="Successfully compiled "+addon_tree.sn_graphs[0].name+"!")
        else:
            self.report({"WARNING"},message="There are errors in "+addon_tree.sn_graphs[0].name+"!")
                
        for a in context.screen.areas: a.tag_redraw()
        return {"FINISHED"}



class SN_OT_RemoveAddon(bpy.types.Operator):
    bl_idname = "sn.remove_addon"
    bl_label = "Remove Addon"
    bl_description = "Removes this compiled addon"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    @classmethod
    def poll(cls, context):
        addon_tree = context.scene.sn.addon_tree()
        return addon_tree != None and addon_is_registered(addon_tree) and not addon_tree.sn_graphs[0].autocompile

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        
        remove_addon(addon_tree)
        addon_tree.set_changes(True)
        
        for a in context.screen.areas: a.tag_redraw()
        return {"FINISHED"}