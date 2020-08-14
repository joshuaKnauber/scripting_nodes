import bpy


class SN_PT_AddonInfoPanel(bpy.types.Panel):
    """Creates a panel that lets you edit the Addon Info for the current NodeTree"""
    bl_label = "Addon Info"
    bl_order = 1
    bl_idname = "SN_PT_AddonInfoPanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Visual Scripting"

    @classmethod
    def poll(cls, context):
        if context.space_data.tree_type == 'ScriptingNodesTree':
            return context.space_data.node_tree != None

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Name")
        col.prop(context.space_data.node_tree, "addon_name", text="")
        col.separator()
        col.label(text="Author")
        col.prop(context.space_data.node_tree, "addon_author", text="")
        col.separator()
        col.label(text="Description")
        col.prop(context.space_data.node_tree, "addon_description", text="")
        col.separator()
        col.label(text="Location")
        col.prop(context.space_data.node_tree, "addon_location", text="")
        col.separator()
        col.label(text="Wiki")
        col.prop(context.space_data.node_tree, "addon_wiki", text="")
        col.separator()
        col.label(text="Warning")
        col.prop(context.space_data.node_tree, "addon_warning", text="")
        col.separator()
        col.label(text="Category")
        col.prop(context.space_data.node_tree, "addon_category", text="")
        col.separator()
        col.label(text="Blender version")
        row = col.row()
        row.prop(context.space_data.node_tree, "addon_blender", text="")
        col.label(text="Addon version")
        row = col.row()
        row.prop(context.space_data.node_tree, "addon_version", text="")

        layout.separator()
        layout.prop(context.space_data.node_tree,"compile_on_start")




        layout.operator("visual_scripting.create_panel_locations")
