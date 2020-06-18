import bpy

class SN_OT_ClearIcon(bpy.types.Operator):
    bl_idname = "scripting_nodes.clear_icon"
    bl_label = "Clear The Icon"
    bl_description = "Clear the icon"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    node_name: bpy.props.StringProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        context.space_data.node_tree.nodes[self.node_name].icon = ""
        return {"FINISHED"}

class SN_OT_SelectIcon(bpy.types.Operator):
    bl_idname = "scripting_nodes.select_icon"
    bl_label = "Select This Icon"
    bl_description = "Select This icon"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    node_name: bpy.props.StringProperty(options={"HIDDEN"})
    icon: bpy.props.StringProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        context.space_data.node_tree.nodes[self.node_name].icon = self.icon
        self.report({"INFO"},message="Selected icon "+self.icon)
        return {"FINISHED"}


class SN_OT_ChooseIcon(bpy.types.Operator):
    bl_idname = "scripting_nodes.choose_icon"
    bl_label = "Choose An Icon"
    bl_description = "Choose an icon"
    bl_options = {"REGISTER","INTERNAL","UNDO"}

    node_name: bpy.props.StringProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {"FINISHED"}
    
    def draw(self, context):
        icons = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys()

        grid = self.layout.grid_flow(align=True,even_columns=True, even_rows=True)
        for icon in icons:
            op = grid.operator("scripting_nodes.select_icon",text="", icon=icon)
            op.node_name = self.node_name
            op.icon = icon

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self,width=900)