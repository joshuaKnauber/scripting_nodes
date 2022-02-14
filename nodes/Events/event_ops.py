import bpy


class SN_OT_RunEventButton(bpy.types.Operator):
    bl_idname = "sn.run_event"
    bl_label = "Run Event"
    bl_description = "Run the event code without triggering event"
    bl_options = {"REGISTER", "INTERNAL"}

    uid: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        if not self.uid in bpy.context.scene.sn.node_function_cache:
            self.report({'WARNING'}, "Failed when trying to run event. Try recompiling!")
            return {"CANCELLED"}
        bpy.context.scene.sn.node_function_cache[self.uid](None)

        return {"FINISHED"}
     
