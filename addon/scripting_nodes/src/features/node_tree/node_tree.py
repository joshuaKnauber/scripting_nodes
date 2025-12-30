import re
from scripting_nodes.src.lib.utils.uuid import get_short_id
from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import (
    node_by_id,
    scripting_node_trees,
    sn_nodes,
)
from scripting_nodes.src.lib.utils.sockets.sockets import (
    from_nodes,
    from_socket,
    to_nodes,
)
from scripting_nodes.src.lib.utils.is_sn import is_sn
import bpy


PREVIOUS_LINKS = {}
PREVIOUS_INTERFACE_STATE = {}


def get_interface_state(tree):
    """Get a hashable representation of the interface state."""
    if not hasattr(tree, "interface"):
        return None
    state = []
    for item in tree.interface.items_tree:
        if hasattr(item, "in_out"):
            # Include socket type, name, and direction
            state.append(
                (
                    getattr(item, "bl_socket_idname", ""),
                    item.name,
                    item.in_out,
                )
            )
    return tuple(state)


class ScriptingNodeTree(bpy.types.NodeTree):
    bl_idname = "ScriptingNodeTree"
    bl_label = "Scripting Node Editor"
    bl_icon = "FILE_SCRIPT"
    is_sn = True
    type: bpy.props.EnumProperty(
        items=[("SCRIPTING", "Scripting", "Scripting")], name="Type"
    )

    initialized: bpy.props.BoolProperty(default=False)
    id: bpy.props.StringProperty(default="")
    is_dirty: bpy.props.BoolProperty(default=True)
    pause_updates: bpy.props.BoolProperty(default=False)

    # Indicates this tree is a group (used as a group node)
    is_group: bpy.props.BoolProperty(default=False)

    # Socket types that should NOT appear in the interface socket type dropdown
    # These are flow sockets that don't make sense for group inputs/outputs
    _EXCLUDED_SOCKET_TYPES = {
        "ScriptingInterfaceSocket",
        "ScriptingProgramSocket",
        "ScriptingLogicSocket",
        "ScriptingBaseSocket",
    }

    @classmethod
    def valid_socket_type(cls, idname):
        """Filter socket types shown in the interface panel dropdown.

        Only data sockets (not flow sockets) should be available for
        group inputs/outputs.
        """
        if not idname.startswith("Scripting"):
            return False
        return idname not in cls._EXCLUDED_SOCKET_TYPES

    @property
    def module_name(self):
        def clean_name(name):
            return (
                re.sub(r"[^a-zA-Z\s]", "", name).replace(" ", "_").lower()
                or "sn_module"
            )

        cleaned_name = clean_name(self.name)
        names = [*map(lambda n: clean_name(n.name), scripting_node_trees())]
        same_names = [n for n in names if n == cleaned_name]
        return f"{cleaned_name}_{self.id}" if len(same_names) > 1 else cleaned_name

    def init(self):
        self.name = "Node Tree"
        self.id = get_short_id()
        self.use_fake_user = True
        self.initialized = True

    def update(self):
        if self.pause_updates:
            return
        self.update_links()
        self.update_group_sockets()
        self.update_node_references()
        bpy.app.timers.register(lambda: self.update_reroutes(), first_interval=0.001)

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

    def update_group_sockets(self, force=False):
        # Check if interface has actually changed
        current_state = get_interface_state(self)
        previous_state = PREVIOUS_INTERFACE_STATE.get(self)

        if not force and current_state == previous_state:
            # No interface changes, skip updating
            return

        # Update stored state
        PREVIOUS_INTERFACE_STATE[self] = current_state

        # update group nodes in all scripting node trees
        # This notifies nodes when the interface sockets of a tree change
        group_node_types = {
            "SNA_Node_Group",
        }
        input_node_types = {
            "SNA_Node_GroupInput",
        }
        output_node_types = {
            "SNA_Node_GroupOutput",
        }

        # Find all nodes that reference function/group trees
        referencing_nodes = [
            node
            for tree in scripting_node_trees()
            for node in sn_nodes(tree)
            if node.bl_idname in group_node_types
        ]
        # Find input/output nodes in this tree
        input_nodes = [
            node for node in self.nodes if node.bl_idname in input_node_types
        ]
        output_nodes = [
            node for node in self.nodes if node.bl_idname in output_node_types
        ]
        for node in [*referencing_nodes, *input_nodes, *output_nodes]:
            node.on_group_socket_change(self)

    def update_node_references(self):
        # Safety check - ensure scene.sna is fully initialized
        if not hasattr(bpy.context.scene, "sna") or not hasattr(
            bpy.context.scene.sna, "references"
        ):
            return

        for node in sn_nodes(self):
            # update existing reference
            for ref in bpy.context.scene.sna.references:
                if ref.node_id == node.id:
                    ref.name = f"{node.name} ({self.name})"
                    break
            # create new reference
            else:
                ref = bpy.context.scene.sna.references.add()
                ref.name = f"{node.name} ({self.name})"
                ref.node_id = node.id
        # remove stale references
        for index in range(len(bpy.context.scene.sna.references) - 1, -1, -1):
            node = node_by_id(bpy.context.scene.sna.references[index].node_id)
            if node is None:
                bpy.context.scene.sna.references.remove(index)

    def update_reroutes(self):
        for node in self.nodes:
            if node.bl_idname == "NodeReroute":
                connected = from_socket(node.inputs[0])
                if connected and node.socket_idname != connected.bl_idname:
                    node.socket_idname = connected.bl_idname
                elif not connected and node.socket_idname != "ScriptingDataSocket":
                    node.socket_idname = "ScriptingDataSocket"
