import bpy


class ScriptingNodeTree(bpy.types.NodeTree):
    bl_idname = "ScriptingNodeTree"
    bl_label = "Scripting Node Editor"
    bl_icon = "FILE_SCRIPT"
    is_sn_ntree = True
    type: bpy.props.EnumProperty(
        items=[("SCRIPTING", "Scripting", "Scripting")], name="Type"
    )
