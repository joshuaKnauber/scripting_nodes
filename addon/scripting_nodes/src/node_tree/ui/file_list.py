import bpy

from ...core import errors, folders
from ...settings.scripts import draw_script
from ..editor import is_sn_editor
from ..file_list import FOLDER, SCRIPT, TREE, active, layout_rows, row_entry


class SNA_UL_Files(bpy.types.UIList):
    """The add-on's node trees and scripts in their folders
    (node_tree/file_list.py). Double click renames."""

    bl_idname = "SNA_UL_Files"

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        shown = row_entry(context.scene.sna.addon, item)
        if shown is None:
            return
        row = layout.row(align=True)
        if shown.kind == FOLDER:
            folder = shown.item
            for _ in folders.split(folders.parent(folder.path)):
                row.label(text="", icon="BLANK1")
            arrow = "DISCLOSURE_TRI_DOWN" if folder.expanded else "DISCLOSURE_TRI_RIGHT"
            row.prop(folder, "expanded", text="", icon=arrow, emboss=False)
            row.prop(folder, "name", text="", emboss=False, icon="FILE_FOLDER")
            return
        # one step per folder, and one for the folders' arrows
        for _ in range(len(folders.split(shown.path)) + 1):
            row.label(text="", icon="BLANK1")
        if shown.kind == TREE:
            tree = shown.item
            icon = "NODETREE" if tree.is_function else "FILE_SCRIPT"
            row.prop(tree, "name", text="", emboss=False, icon=icon)
            return
        script = shown.item
        if script.source_type == "INTERNAL" and script.text_block is not None:
            row.prop(script.text_block, "name", text="", emboss=False, icon="TEXT")
        else:
            row.label(text=shown.name, icon="TEXT")
        if errors.node_message(script.id):
            row.label(text="", icon="ERROR")

    def filter_items(self, context, data, propname):
        laid_out = layout_rows(context.scene, self.filter_name)
        flags = [
            self.bitflag_filter_item if visible else 0 for _, _, visible in laid_out
        ]
        order = sorted(range(len(laid_out)), key=lambda i: laid_out[i][0])
        new_order = [0] * len(laid_out)
        for position, index in enumerate(order):
            new_order[index] = position
        return flags, new_order


class SNA_MT_AddFile(bpy.types.Menu):
    bl_idname = "SNA_MT_AddFile"
    bl_label = "Add"

    def draw(self, context):
        layout = self.layout
        layout.operator("sna.add_node_tree", text="Node Tree", icon="FILE_SCRIPT")
        layout.operator("sna.add_script", text="Script", icon="TEXT")
        layout.separator()
        layout.operator("sna.add_folder", text="Folder", icon="NEWFOLDER")


class SNA_PT_Files(bpy.types.Panel):
    bl_idname = "SNA_PT_Files"
    bl_label = "Files"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return is_sn_editor(context)

    def draw(self, context):
        layout = self.layout
        ui = context.scene.sna.ui

        row = layout.row()
        row.template_list("SNA_UL_Files", "", ui, "files", ui, "active_file", rows=7)

        col = row.column(align=True)
        col.menu("SNA_MT_AddFile", icon="ADD", text="")
        col.operator("sna.remove_file", icon="REMOVE", text="")
        col.separator()
        col.operator_menu_enum(
            "sna.move_to_folder", "folder", icon="FOLDER_REDIRECT", text=""
        )
        col.separator()
        col.operator("wm.append", icon="APPEND_BLEND", text="")

        selected = active(context)
        if selected is not None and selected.kind == SCRIPT:
            draw_script(layout.column(), selected.item)
