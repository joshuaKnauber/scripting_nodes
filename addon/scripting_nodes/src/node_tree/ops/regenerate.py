import bpy

from ...core import scheduler


class SNA_OT_RegenerateAllNodes(bpy.types.Operator):
    bl_idname = "sna.regenerate"
    bl_label = "Rebuild Addon"
    bl_description = "Rebuild the generated addon and reload it"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context: bpy.types.Context):
        scheduler.request_full()
        scheduler.flush()
        self.report({"INFO"}, "Rebuilt the addon")
        return {"FINISHED"}
