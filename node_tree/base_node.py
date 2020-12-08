import bpy


class SN_ScriptingBaseNode:

    bl_width_min = 40
    bl_width_default = 160
    bl_width_max = 5000
    node_color = (0.5,0.5,0.5)


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'