import bpy


class SN_ScriptingBaseNode:
    bl_width_min = 40
    bl_width_default = 160
    bl_width_max = 5000

    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'

    def update(self):
        pass
    
    def evaluate(self, output):
        pass

    def get_register_block(self):
        pass

    def needed_imports(self):
        return ["bpy"]