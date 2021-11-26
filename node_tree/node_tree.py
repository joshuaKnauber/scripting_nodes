import bpy


class ScriptingNodesTree(bpy.types.NodeTree):

    bl_idname = 'ScriptingNodesTree'
    bl_label = "Visual Scripting"
    bl_icon = 'FILE_SCRIPT'

    # variables: bpy.props.CollectionProperty()

    def update(self):
        print("update node tree")