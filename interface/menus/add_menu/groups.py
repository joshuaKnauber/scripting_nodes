import bpy

from ....core.nodes.Group.GroupNode import SNA_NodeGroupNode


class SNA_MT_GroupMenu(bpy.types.Menu):
    bl_idname = "SNA_MT_GroupMenu"
    bl_label = "Group"

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        op = layout.operator("node.add_node", text="Group")
        op.type = SNA_NodeGroupNode.bl_idname
        op.use_transform = True

        op = layout.operator("node.add_node", text="Group Input")
        op.type = "NodeGroupInput"
        op.use_transform = True

        op = layout.operator("node.add_node", text="Group Output")
        op.type = "NodeGroupOutput"
        op.use_transform = True
