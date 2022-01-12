import bpy



class SN_OT_AddProperty(bpy.types.Operator):
    bl_idname = "sn.add_property"
    bl_label = "Add Property"
    bl_description = "Adds a property to the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        sn = context.scene.sn
        new_prop = sn.properties.add()
        new_prop.name = "New Property"
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
        sn.properties[sn.property_index].unregister_all()
        sn.properties.remove(sn.property_index)
        sn.property_index -= 1
        if len(sn.properties):
            sn.properties[0].register_all()
        return {"FINISHED"}



class SN_OT_RemoveGroupProperty(bpy.types.Operator):
    bl_idname = "sn.remove_group_property"
    bl_label = "Remove Property"
    bl_description = "Removes this property from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    group_items_path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        items = eval(self.group_items_path)
        items.remove(self.index)
        return {"FINISHED"}



class SN_OT_MoveProperty(bpy.types.Operator):
    bl_idname = "sn.move_property"
    bl_label = "Move Property"
    bl_description = "Moves this property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    move_up: bpy.props.BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        sn = context.scene.sn
        if self.move_up:
            sn.properties.move(sn.property_index, sn.property_index - 1)
            sn.property_index -= 1
        else:
            sn.properties.move(sn.property_index, sn.property_index + 1)
            sn.property_index += 1
        return {"FINISHED"}



class SN_OT_MoveGroupProperty(bpy.types.Operator):
    bl_idname = "sn.move_group_property"
    bl_label = "Move Property"
    bl_description = "Moves this property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    group_items_path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})
    move_up: bpy.props.BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        items = eval(self.group_items_path)
        if self.move_up:
            items.move(self.index, self.index - 1)
        else:
            items.move(self.index, self.index + 1)
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



class SN_OT_AddEnumItem(bpy.types.Operator):
    bl_idname = "sn.add_enum_item"
    bl_label = "Add Enum Item"
    bl_description = "Adds an enum item to this property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    item_data_path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        items = eval(self.item_data_path)
        item = items.add()
        item.update(context)
        return {"FINISHED"}



class SN_OT_AddPropertyItem(bpy.types.Operator):
    bl_idname = "sn.add_property_item"
    bl_label = "Add Property"
    bl_description = "Adds a property to this group"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    group_data_path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        prop = eval(self.group_data_path)
        new_prop = prop.settings.properties.add()
        new_prop.name = "New Property"
        return {"FINISHED"}