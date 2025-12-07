import bpy
from ...interface.panels.property_ui_list import get_selected_property


class SN_PropertyCategory(bpy.types.PropertyGroup):

    def set_name(self, value):
        current_name = self.get("_name", "New Category")
        for prop in bpy.context.scene.sn.properties:
            if prop.category and prop.category == current_name:
                prop.category = value
        self["_name"] = value

    def get_name(self):
        return self.get("_name", "New Category")

    name: bpy.props.StringProperty(
        name="Name",
        default="New Category",
        description="The name of this property category",
        set=set_name,
        get=get_name,
    )


class SN_OT_AddPropertyCategory(bpy.types.Operator):
    bl_idname = "sn.add_property_category"
    bl_label = "Add Property Category"
    bl_description = "Adds a property category"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        context.scene.sn.property_categories.add()
        return {"FINISHED"}


class SN_OT_RemovePropertyCategory(bpy.types.Operator):
    bl_idname = "sn.remove_property_category"
    bl_label = "Remove Property Category"
    bl_description = "Removes a property category"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        context.scene.sn.property_categories.remove(self.index)
        return {"FINISHED"}


class SN_OT_EditPropertyCategories(bpy.types.Operator):
    bl_idname = "sn.edit_property_categories"
    bl_label = "Edit Property Categories"
    bl_description = "Edit the addon property categories"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Categories")
        for i, cat in enumerate(context.scene.sn.property_categories):
            row = layout.row()
            row.scale_y = 1.2
            row.prop(cat, "name", text="")
            row.operator(
                "sn.remove_property_category", text="", icon="REMOVE", emboss=False
            ).index = i

        if not context.scene.sn.property_categories:
            row = layout.row()
            row.enabled = False
            row.label(text="No categories added", icon="ERROR")

        row = layout.row()
        row.scale_y = 1.2
        row.operator("sn.add_property_category", text="Add Category", icon="ADD")

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=250)


class SN_OT_MovePropertyToCategory(bpy.types.Operator):
    bl_idname = "sn.move_property_to_category"
    bl_label = "Move Property Category"
    bl_description = "Move the selected property to a different category"
    bl_options = {"REGISTER", "INTERNAL"}

    category: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        prop = get_selected_property()
        if prop:
            if self.category == -1:
                prop.category = "OTHER"
            else:
                prop.category = context.scene.sn.property_categories[self.category].name
        context.area.tag_redraw()
        return {"FINISHED"}


class SN_OT_MovePropertyCategory(bpy.types.Operator):
    bl_idname = "sn.move_property_category"
    bl_label = "Move Property Category"
    bl_description = "Move the selected property to a different category"
    bl_options = {"REGISTER", "INTERNAL"}

    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        prop = get_selected_property()

        layout.label(text="Categories")
        for i, cat in enumerate(context.scene.sn.property_categories):
            row = layout.row()
            row.enabled = prop != None and prop.category != cat.name
            row.scale_y = 1.2
            row.operator(
                "sn.move_property_to_category",
                text=f"Move to '{cat.name}'",
                icon="FORWARD",
            ).category = i

        row = layout.row()
        row.enabled = prop != None and prop.category and prop.category != "OTHER"
        row.scale_y = 1.2
        row.operator(
            "sn.move_property_to_category", text=f"Remove Category", icon="REMOVE"
        ).category = -1

        if not len(context.scene.sn.property_categories):
            row = layout.row()
            row.enabled = False
            row.label(text="No categories added", icon="ERROR")

    def invoke(self, context, event):
        context.scene.sn.property_index = self.index
        return context.window_manager.invoke_popup(self, width=250)
