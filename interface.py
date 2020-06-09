import bpy
from .properties.property_utils import sn_props, error_props
from textwrap import wrap

def node_tree_header(self, context):
    if context.space_data.tree_type == 'ScriptingNodesTree':
        layout = self.layout
        row = layout.row(align=True)
        row.scale_x = 1.3
        if context.space_data.node_tree != None:
            row.operator("scripting_nodes.remove_nodetree", icon='TRASH', text="")
            row.separator()
            row.operator("scripting_nodes.compile", icon='FILE_REFRESH')
            row.operator("scripting_nodes.unregister", icon='UNLINKED', text="")
            row.separator()
            row.prop(sn_props(),"auto_compile")
        row.prop(sn_props(), "examples", icon='LINENUMBERS_ON', text="")

class SN_PT_ExportPanel(bpy.types.Panel):
    """Creates a panel that lets you export the addon and the current NodeTree"""
    bl_label = "Export"
    bl_order = 0
    bl_idname = "SN_PT_ExportPanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Visual Scripting"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.space_data.tree_type == 'ScriptingNodesTree':
            return context.space_data.node_tree != None

    def draw(self, context):
        layout = self.layout
        tree = context.space_data.node_tree
        name = tree.addon_name.lower().replace(" ","_") + ".py"
        text = True
        try:
            bpy.data.texts[name]
        except:
            text = False
        if text:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("scripting_nodes.export_addon", text="Export addon",icon="EXPORT")
        else:
            layout.label(text="Reload the addon before exporting!")


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

class SN_PT_ErrorLogPanel(bpy.types.Panel):
    """Creates a panel for displaying error messages in the node editors sidebar"""
    bl_label = "Errors"
    bl_order = 2
    bl_idname = "SN_PT_ErrorLogPanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Visual Scripting"

    @classmethod
    def poll(cls, context):
        if context.space_data.tree_type == 'ScriptingNodesTree':
            return context.space_data.node_tree != None


    def draw_error(self, layout, error_type, error_message, fatal, node):
        box = layout.box()
        col = box.column(align=True)

        row = col.row()
        if node != "":
            row.operator("scripting_nodes.find_error_node",text="",emboss=False,icon="NODE").node_name = node

        row.alert = fatal
        row.label(text=error_type)

        line_length = bpy.context.region.width // sn_props().line_width
        error_message = wrap(error_message,line_length)

        for line in error_message:
            col.label(text=line)

    def draw_header(self,context):
        self.layout.prop(sn_props(),"show_line_width",text="",icon="PREFERENCES",emboss=False)

    def draw(self, context):
        layout = self.layout

        if sn_props().show_line_width:
            box = layout.box()
            box.prop(sn_props(),"line_width",slider=True,text="Line breaks")

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
