from .compiler_data import gpl_block, addon_info, error_logs, import_texts
from bpy_extras.io_utils import ExportHelper
import bpy
import os
from ..properties.property_utils import sn_props
from ..node_categories import compiler


class SN_OT_EmptyOperator(bpy.types.Operator):
    bl_idname = "scripting_nodes.empty"
    bl_label = "Empty Operator"
    bl_description = "This is an empty operator"
    bl_options = {"REGISTER","INTERNAL"}

    def execute(self, context):        
        return {"FINISHED"}


class SN_OT_ReloadButton(bpy.types.Operator):
    bl_idname = "scripting_nodes.compile"
    bl_label = "Reload"
    bl_description = "Compiles the Nodetree"
    bl_options = {"REGISTER","INTERNAL", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        compiler().recompile()
        return {"FINISHED"}


class SN_OT_UnregisterButton(bpy.types.Operator):
    bl_idname = "scripting_nodes.unregister"
    bl_label = "Unregister"
    bl_description = "Unregister the Nodetree"
    bl_options = {"REGISTER","INTERNAL", "UNDO"}

    @classmethod
    def poll(cls, context):
        return compiler().is_registered()

    def execute(self, context):
        compiler().reset_file()
        return {"FINISHED"}


class SN_OT_FindErrorNode(bpy.types.Operator):
    bl_idname = "scripting_nodes.find_error_node"
    bl_label = "Find error node"
    bl_description = "Finds the node which is causing the error"
    bl_options = {"REGISTER","INTERNAL"}

    node_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        found = False
        if context.space_data.tree_type == "ScriptingNodesTree":
            for node in context.space_data.node_tree.nodes:
                if node.name == self.node_name:
                    found = True
                    node.select = True
                    bpy.ops.node.view_selected()
                else:
                    node.select = False
        if not found:
            self.report({"INFO"},message ="Couldn't find the corresponding node. Try to reload the node tree.")
        return {"FINISHED"}


class SN_OT_RemoveButton(bpy.types.Operator):
    bl_idname = "scripting_nodes.remove_nodetree"
    bl_label = "Delete"
    bl_description = "Delete the active Nodetree"
    bl_options = {"REGISTER","INTERNAL", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        treeName = context.space_data.node_tree.name
        compiler().reset_file()
        bpy.data.node_groups.remove(bpy.data.node_groups[treeName])
        if len(bpy.data.node_groups) > 0:
            context.space_data.node_tree = bpy.data.node_groups[0]
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class SN_OT_ExportAddonButton(bpy.types.Operator, ExportHelper):
    bl_idname = "scripting_nodes.export_addon"
    bl_label = "Export Addon"
    bl_description = "Export the addon file"
    bl_options = {"REGISTER","INTERNAL"}

    filepath: bpy.props.StringProperty(name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    filename_ext = ".py"
    filter_glob: bpy.props.StringProperty(default='*.py', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        path = bpy.utils.user_resource('SCRIPTS', "addons") + "//"
        tree = bpy.context.space_data.node_tree
        name = tree.addon_name.lower().replace(" ","_")
        path+= name
        self.filepath = path
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        filepath = self.filepath
        if filepath.split(".")[-1] != "py":
            return {"CANCELLED"}
        else:
            tree = context.space_data.node_tree
            name = tree.addon_name.lower().replace(" ","_") + ".py"
            text = bpy.data.texts[name]
            text = text.lines[:-2]

            basedir = os.path.dirname(filepath)
            if not os.path.exists(basedir):
                os.makedirs(basedir)

            newFile = open(filepath, "w")
            newFile.truncate(0)
            for line in text:
                newFile.write(line.body)
                newFile.write("\n")

            return {"FINISHED"}