import bpy
from ...interface.panels.graph_ui_list import get_selected_graph


class SN_GraphCategory(bpy.types.PropertyGroup):

    def set_name(self, value):
        current_name = self.get("_name", "New Category")
        for ntree in bpy.data.node_groups:
            if hasattr(ntree, "category"):
                if ntree.category and ntree.category == current_name:
                    ntree.category = value
        self["_name"] = value

    def get_name(self):
        return self.get("_name", "New Category")
    
    name: bpy.props.StringProperty(name="Name", default="New Category",
                            description="The name of this graph category",
                            set=set_name, get=get_name)


class SN_OT_AddGraphCategory(bpy.types.Operator):
    bl_idname = "sn.add_graph_category"
    bl_label = "Add Graph Category"
    bl_description = "Adds a graph category"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        context.scene.sn.graph_categories.add()
        return {"FINISHED"}
    
    
    
class SN_OT_RemoveGraphCategory(bpy.types.Operator):
    bl_idname = "sn.remove_graph_category"
    bl_label = "Remove Graph Category"
    bl_description = "Removes a graph category"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}
    
    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        context.scene.sn.graph_categories.remove(self.index)
        return {"FINISHED"}

    
    
class SN_OT_EditGraphCategories(bpy.types.Operator):
    bl_idname = "sn.edit_graph_categories"
    bl_label = "Edit Graph Categories"
    bl_description = "Edit the addon graph categories"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Categories")
        for i, cat in enumerate(context.scene.sn.graph_categories):
            row = layout.row()
            row.scale_y = 1.2
            row.prop(cat, "name", text="")
            row.operator("sn.remove_graph_category", text="", icon="REMOVE", emboss=False).index = i

        if not context.scene.sn.graph_categories:
            row = layout.row()
            row.enabled = False
            row.label(text="No categories added", icon="ERROR")

        row = layout.row()
        row.scale_y = 1.2
        row.operator("sn.add_graph_category", text="Add Category", icon="ADD")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=250)

    
    
class SN_OT_MoveGraphToCategory(bpy.types.Operator):
    bl_idname = "sn.move_graph_to_category"
    bl_label = "Move Graph Category"
    bl_description = "Move the selected graph to a different category"
    bl_options = {"REGISTER", "INTERNAL"}
    
    category: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ntree = get_selected_graph()
        if ntree:
            if self.category == -1:
                ntree.category = "OTHER"
            else:
                ntree.category = context.scene.sn.graph_categories[self.category].name
        context.area.tag_redraw()
        return {"FINISHED"}

    
    
class SN_OT_MoveGraphCategory(bpy.types.Operator):
    bl_idname = "sn.move_graph_category"
    bl_label = "Move Graph Category"
    bl_description = "Move the selected graph to a different category"
    bl_options = {"REGISTER", "INTERNAL"}
    
    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        ntree = get_selected_graph()

        layout.label(text="Categories")
        for i, cat in enumerate(context.scene.sn.graph_categories):
            row = layout.row()
            row.enabled = ntree != None and ntree.category != cat.name
            row.scale_y = 1.2
            row.operator("sn.move_graph_to_category", text=f"Move to '{cat.name}'", icon="FORWARD").category = i

        row = layout.row()
        row.enabled = ntree != None and ntree.category and ntree.category != "OTHER"
        row.scale_y = 1.2
        row.operator("sn.move_graph_to_category", text=f"Remove Category", icon="REMOVE").category = -1

        if not len(context.scene.sn.graph_categories):
            row = layout.row()
            row.enabled = False
            row.label(text="No categories added", icon="ERROR")
    
    def invoke(self, context, event):
        context.scene.sn.node_tree_index = self.index
        return context.window_manager.invoke_popup(self, width=250)

