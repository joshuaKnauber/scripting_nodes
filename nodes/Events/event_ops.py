import bpy
import atexit


class SN_OT_RunEventButton(bpy.types.Operator):
    bl_idname = "sn.run_event"
    bl_label = "Run Event"
    bl_description = "Run the event code without triggering event"
    bl_options = {"REGISTER", "INTERNAL"}

    uid: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    handler: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def get_atexit_functions(self):
        funs = []

        class Capture:
            def __eq__(self, other):
                funs.append(other)
                return False

        c = Capture()
        atexit.unregister(c)
        return funs

    def execute(self, context):
        if self.handler == "EXIT":
            for func in self.get_atexit_functions():
                if self.uid in func.__name__:
                    func(None)
                    return {"FINISHED"}
        
        else:
            handlers = getattr(bpy.app.handlers, self.handler)
            for handler in handlers:
                if self.uid in handler.__name__:
                    handler(None)
                    return {"FINISHED"}
                
        self.report({'WARNING'}, "Failed when trying to run event. Try recompiling!")
        return {"CANCELLED"}