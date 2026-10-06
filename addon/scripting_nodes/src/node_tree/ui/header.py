from ..editor import in_sn_tree
import bpy


def header_append(self, context):
    if in_sn_tree(context):
        self.layout.operator("sna.regenerate", text="", icon="FILE_REFRESH")


def register():
    bpy.types.NODE_HT_header.append(header_append)


def unregister():
    bpy.types.NODE_HT_header.remove(header_append)
