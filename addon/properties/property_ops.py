import bpy



class SN_OT_AddProperty(bpy.types.Operator):
    bl_idname = "sn.add_property"
    bl_label = "Add Property"
    bl_description = "Adds a property to the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        sn = context.scene.sn
        new_prop = sn.properties.add()
        for index, property in enumerate(sn.properties):
            if property == new_prop:
                sn.property_index = index
        return {"FINISHED"}



class SN_OT_RemoveProperty(bpy.types.Operator):
    bl_idname = "sn.remove_property"
    bl_label = "Remove Property"
    bl_description = "Removes this property from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return context.scene.sn.property_index < len(context.scene.sn.properties)

    def execute(self, context):
        sn = context.scene.sn
        sn.properties.remove(sn.property_index)
        sn.property_index -= 1
        return {"FINISHED"}



class SN_OT_CopyPythonName(bpy.types.Operator):
    bl_idname = "sn.copy_python_name"
    bl_label = "Copy Python Name"
    bl_description = "Copies the python name of this item to use in scripts"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    name: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        context.window_manager.clipboard = self.name
        self.report({"INFO"}, message="Copied!")
        return {"FINISHED"}