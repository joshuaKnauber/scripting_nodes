import bpy
from .properties.property_utils import sn_props, error_props

def node_tree_header(self, context):
    if context.space_data.tree_type == 'ScriptingNodesTree' and context.space_data.node_tree != None:
        layout = self.layout
        row = layout.row(align=True)
        row.scale_x = 1.3

        
        row.separator()
        row.operator("scripting_nodes.compile", icon='FILE_REFRESH')
        row.separator()
        row.prop(sn_props(),"auto_compile")
        row.prop(sn_props(), "examples", icon='LINENUMBERS_ON', text="")

class SN_PT_AddonInfoPanel(bpy.types.Panel):
    """Creates a panel that lets you edit the Addon Info for the current NodeTree"""
    bl_label = "Addon Info"
    bl_order = 0
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

class SN_PT_ErrorLogPanel(bpy.types.Panel):
    """Creates a panel for displaying error messages in the node editors sidebar"""
    bl_label = "Errors"
    bl_order = 1
    bl_idname = "SN_PT_ErrorLogPanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Visual Scripting"

    @classmethod
    def poll(cls, context):
        if context.space_data.tree_type == 'ScriptingNodesTree':
            return context.space_data.node_tree != None

    def get_line_length(self):
        char_width = 15
        return bpy.context.region.width // char_width

    def draw_error(self, layout, error_type, error_message, fatal, node):
        box = layout.box()
        col = box.column(align=True)

        row = col.row()
        if node != "":
            row.operator("scripting_nodes.find_error_node",text="",emboss=False,icon="NODE").node_name = node

        row.alert = fatal
        row.label(text=error_type)

        line_length = self.get_line_length()
        error_message = [error_message[i:i+line_length] for i in range(0, len(error_message), line_length)]

        for line in error_message:
            col.label(text=line)

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=False)

        if len(error_props()) > 0:
            for error in error_props():
                if error.fatal_error:
                    self.draw_error(column, error.error_type, error.error_message, True, error.node)
            for error in error_props():
                if not error.fatal_error:
                    self.draw_error(column, error.error_type, error.error_message, False, error.node)
        else:
            column.label(text="No errors found")
