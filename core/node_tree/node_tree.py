from typing import Any
import bpy

from ...utils.naming import pythonify_name
from ..utils.id import get_id


class ScriptingNodeTree(bpy.types.NodeTree):
    bl_idname = "ScriptingNodeTree"
    bl_label = "Scripting Node Editor"
    bl_icon = "FILE_SCRIPT"
    is_sn_ntree = True
    type: bpy.props.EnumProperty(
        items=[("SCRIPTING", "Scripting", "Scripting")], name="Type"
    )

    is_dirty: bpy.props.BoolProperty(default=False, name="Is Dirty")

    id: bpy.props.StringProperty(
        default="", name="ID", description="Unique ID of the node tree"
    )

    @classmethod
    def valid_socket_type(cls, idname: str | Any) -> bool:
        return idname.startswith("SNA_")

    def _init(self):
        """Called when the node tree is created by the depsgraph handler."""
        if not self.id:
            self.id = get_id()
            self.name = "NodeTree"
            self.use_fake_user = True

    def update(self):
        """Called when the node tree is updating."""
        for ntree in bpy.data.node_groups:
            if getattr(ntree, "is_sn_ntree", False):
                for node in ntree.nodes:
                    if getattr(node, "group_tree", None) == self:
                        node.on_group_tree_update()

    def mark_dirty(self, node: bpy.types.Node):
        self.is_dirty = True

    def _execute_node(self, node_id: str, local_vars: dict, global_vars: dict):
        """Runs the generated code on the given node. Called by nodes during development."""
        for node in self.nodes:
            if getattr(node, "id", None) == node_id:
                node._execute(local_vars, global_vars)
                break

    def function_name(self):
        """Returns the name of the function for this node tree"""
        return f"sna_{pythonify_name(self.name, 'function')}_{self.id}"
