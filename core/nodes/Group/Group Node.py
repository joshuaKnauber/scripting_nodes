import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_NodeGroupNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_NodeGroupNode"
    bl_label = "Node Group"
    bl_width_min = 200

    def poll_tree(self, tree):
        return tree.bl_idname == "ScriptingNodesTree"

    group_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree, poll=poll_tree)

    def draw_node(self, context, layout):
        layout.template_ID(self, "group_tree", new="node.new_node_tree")
