import bpy


class SN_MT_AddNodeMenu(bpy.types.Menu):
    bl_idname = "SN_MT_AddNodeMenu"
    bl_label = "Add Node"

    @classmethod
    def poll(cls, context):
        return context.space_data.node_tree.bl_idname == "ScriptingNodesTree"

    def draw(self, context):
        layout = self.layout

        layout.operator("node.add_search", text="Search", icon="VIEWZOOM")
        layout.separator()

        layout.operator("object.select_all", text="Inverse").action = 'INVERT'
        layout.operator("object.select_random", text="Random")