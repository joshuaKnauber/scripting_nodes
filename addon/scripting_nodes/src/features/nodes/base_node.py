from typing import Literal, Set
from scripting_nodes.src.lib.utils.uuid import get_short_id
from scripting_nodes.src.features.node_tree.node_tree import ScriptingNodeTree
import bpy


class SNA_BaseNode(bpy.types.Node):

    @classmethod
    def poll(cls, ntree):
        """Checks if the node is valid"""
        return ntree.bl_idname == ScriptingNodeTree.bl_idname

    def ntree_poll(self, group):
        """Checks if the node tree is valid"""
        return group.bl_idname == ScriptingNodeTree.bl_idname

    @property
    def node_tree(self):
        """Returns the node tree this node lives in"""
        return self.id_data

    ### Properties

    is_sn = True

    sn_options: Set[Literal["ROOT_NODE"]] = {}

    id: bpy.props.StringProperty(
        default="", name="ID", description="Unique ID of the node"
    )

    code: bpy.props.StringProperty()

    ### Life Cycle

    def init(self, context: bpy.types.Context):
        """Called when the node is created"""
        self.id = get_short_id()
        self.on_create()
        self._generate()

    def on_create(self):
        pass

    def copy(self, node: bpy.types.Node):
        """Called when the node is copied"""
        self.id = get_short_id()
        self._generate()

    def free(self):
        """Called when the node is deleted"""
        self.node_tree.is_dirty = True

    ### Code Generation

    def _generate(self):
        self.generate()
        self.node_tree.is_dirty = True

    def generate(self):
        pass
