import bpy

from ....utils.is_serpens import in_sn_tree
from ....core.nodes.Group.GroupNode import SNA_NodeGroupNode
from ....core.nodes.Group.GroupInput import SNA_NodeGroupInputNode
from ....core.nodes.Group.GroupOutput import SNA_NodeGroupOutputNode


class SNA_MT_GroupMenu(bpy.types.Menu):
    bl_idname = "SNA_MT_GroupMenu"
    bl_label = "Group"

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        op = layout.operator("node.add_node", text="Group")
        op.type = SNA_NodeGroupNode.bl_idname
        op.use_transform = True

        op = layout.operator("node.add_node", text="Group bl")
        op.type = "NodeCustomGroup"
        op.use_transform = True

        op = layout.operator("node.add_node", text="Group Input")
        op.type = SNA_NodeGroupInputNode.bl_idname
        op.use_transform = True

        op = layout.operator("node.add_node", text="Group Input bl")
        op.type = "NodeGroupInput"
        op.use_transform = True

        op = layout.operator("node.add_node", text="Group Output")
        op.type = SNA_NodeGroupOutputNode.bl_idname
        op.use_transform = True

        op = layout.operator("node.add_node", text="Group Output bl")
        op.type = "NodeGroupOutput"
        op.use_transform = True
