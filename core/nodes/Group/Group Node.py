import bpy

from ....core.node_tree.node_tree import ScriptingNodeTree
from ..base_node import SNA_BaseNode


class SNA_NodeGroupNode(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeGroupNode"
    bl_label = "Node Group"
    bl_width_min = 200

    def poll_tree(self, tree):
        return tree.bl_idname == ScriptingNodeTree.bl_idname

    group_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree, poll=poll_tree)

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()

    def draw_node(self, context, layout):
        layout.template_ID(self, "group_tree", new="node.new_node_tree")
