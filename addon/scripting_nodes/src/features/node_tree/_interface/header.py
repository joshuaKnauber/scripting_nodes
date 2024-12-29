from scripting_nodes.src.lib.editor.editor import in_sn_tree
import bpy


def header_prepend(self, context):
    if in_sn_tree(context):
        layout = self.layout
        row = layout.row()


def header_append(self, context):
    if in_sn_tree(context):
        sna = context.scene.sna
        layout = self.layout

        layout.operator("sna.regenerate", text="", icon="FILE_REFRESH")


def register():
    bpy.types.NODE_HT_header.prepend(header_prepend)
    bpy.types.NODE_HT_header.append(header_append)


def unregister():
    bpy.types.NODE_HT_header.remove(header_prepend)
    bpy.types.NODE_HT_header.remove(header_append)
