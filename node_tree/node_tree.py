import bpy


class ScriptingNodesTree(bpy.types.NodeTree):

    bl_idname = 'ScriptingNodesTree'
    bl_label = "Visual Scripting"
    bl_icon = 'FILE_SCRIPT'

    def interface_update(self,context):
        print("interface update")

    def update(self):
        print("update")