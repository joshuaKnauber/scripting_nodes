import bpy


class SN_OT_DummyOperator(bpy.types.Operator):
    bl_idname = "sn.dummy_operator"
    bl_label = "Dummy Operator"
    bl_description = "Dummy Operator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.report({'INFO'}, "Ran Operator")
        return {'FINISHED'}
