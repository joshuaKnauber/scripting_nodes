import bpy


class ScriptingNodesTree(bpy.types.NodeTree):
    bl_idname = "ScriptingNodesTree"
    bl_label = "Visual Scripting Editor"
    bl_icon = "FILE_SCRIPT"
    is_sn = True
    type: bpy.props.EnumProperty(
        items=[("SCRIPTING", "Scripting", "Scripting")], name="Type"
    )

    def update(self):
        pass
