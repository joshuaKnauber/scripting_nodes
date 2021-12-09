import bpy


class SN_OT_ExportSnippet(bpy.types.Operator):
    bl_idname = "sn.export_snippet"
    bl_label = "Export Snippet"
    bl_description = "Export this node as a snippet"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        
        return {"FINISHED"}
