import bpy

class SN_OT_ReloadButton(bpy.types.Operator):
    bl_idname = "scripting_nodes.compile"
    bl_label = "Reload"
    bl_description = "Compiles the Nodetree"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {"FINISHED"}
