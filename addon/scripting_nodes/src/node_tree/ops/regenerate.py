import bpy

from ...core import scheduler


class SNA_OT_RegenerateAllNodes(bpy.types.Operator):
    bl_idname = "sna.regenerate"
    bl_label = "Regenerate All Nodes"
    bl_description = "Regenerate the code of all nodes and reload the addon"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context: bpy.types.Context):
        scheduler.request_full()
        scheduler.flush()
        self.report({"INFO"}, "Regenerated all nodes")
        return {"FINISHED"}
