import re
from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import (
    scripting_node_trees,
    sn_nodes,
)
from scripting_nodes.src.lib.utils.sockets.sockets import from_nodes, to_nodes
from scripting_nodes.src.lib.utils.is_sn import is_sn
import bpy


PREVIOUS_LINKS = {}


class ScriptingNodeTree(bpy.types.NodeTree):
    bl_idname = "ScriptingNodeTree"
    bl_label = "Scripting Node Editor"
    bl_icon = "FILE_SCRIPT"
    is_sn = True
    type: bpy.props.EnumProperty(
        items=[("SCRIPTING", "Scripting", "Scripting")], name="Type"
    )

    initialized: bpy.props.BoolProperty(default=False)
    is_dirty: bpy.props.BoolProperty(default=True)

    @classmethod
    def valid_socket_type(cls, idname):
        return idname.startswith("Scripting")

    @property
    def module_name(self):
        return (
            re.sub(r"[^a-zA-Z\s]", "", self.name).replace(" ", "_").lower()
            or "sn_module"
        )

    def init(self):
        self.name = "Node Tree"
        self.use_fake_user = True
        self.initialized = True

    def update(self):
        self.update_links()
        self.update_group_sockets()

    def update_links(self):
        new_links = set([*map(lambda l: (l, l.from_node, l.to_node), self.links)])
        prev_links = PREVIOUS_LINKS[self] if self in PREVIOUS_LINKS else set()
        if self in PREVIOUS_LINKS:
            # added links
            for _, from_node, to_node in new_links - prev_links:
                if from_node in self.nodes.values():
                    if is_sn(from_node):
                        from_node.ntree_link_created()
                    elif from_node.bl_idname == "NodeReroute":
                        nodes = from_nodes(from_node.inputs[0])
                        for node in nodes:
                            node.ntree_link_created()
                if to_node in self.nodes.values():
                    if is_sn(to_node):
                        to_node.ntree_link_created()
                    elif to_node.bl_idname == "NodeReroute":
                        nodes = to_nodes(to_node.outputs[0])
                        for node in nodes:
                            node.ntree_link_created()
            # removed links
            for _, from_node, to_node in prev_links - new_links:
                if from_node in self.nodes.values():
                    if is_sn(from_node):
                        from_node.ntree_link_removed()
                    elif from_node.bl_idname == "NodeReroute":
                        nodes = from_nodes(from_node.inputs[0])
                        for node in nodes:
                            node.ntree_link_removed()
                if to_node in self.nodes.values():
                    if is_sn(to_node):
                        to_node.ntree_link_removed()
                    elif to_node.bl_idname == "NodeReroute":
                        nodes = to_nodes(to_node.outputs[0])
                        for node in nodes:
                            node.ntree_link_removed()

        # update previous links
        PREVIOUS_LINKS[self] = new_links

    def update_group_sockets(self):
        # update group nodes in all scripting node trees
        group_nodes = [
            node
            for tree in scripting_node_trees()
            for node in sn_nodes(tree)
            if node.bl_idname == "SNA_Node_Group"
        ]
        group_inputs = [
            node for node in self.nodes if node.bl_idname == "SNA_Node_GroupInput"
        ]
        group_outputs = [
            node for node in self.nodes if node.bl_idname == "SNA_Node_GroupOutput"
        ]
        for node in [*group_nodes, *group_inputs, *group_outputs]:
            node.on_group_socket_change(self)
