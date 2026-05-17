import re
from ...lib.utils.uuid import get_short_id
from ...lib.utils.node_tree.scripting_node_trees import (
    node_by_id,
    scripting_node_trees,
    sn_nodes,
)
from ...lib.utils.sockets.sockets import (
    from_nodes,
    from_socket,
    to_nodes,
)
from ...lib.utils.is_sn import is_sn
from ...lib.utils.logger import log
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
    id: bpy.props.StringProperty(default="")
    is_dirty: bpy.props.BoolProperty(default=True)
    pause_updates: bpy.props.BoolProperty(default=False)
    is_group: bpy.props.BoolProperty(
        default=False,
        description=(
            "If true, this tree is a function (node group) - it compiles to a "
            "Python function rather than addon-level code, and is callable from "
            "Group nodes in other trees"
        ),
    )

    @property
    def module_name(self):
        """Stable Python module name for this tree.

        Always suffixed with the tree's id so adding/removing sibling trees
        with the same display name never changes any other tree's module
        name. Renaming the tree itself still rotates the name (handled by
        a separate dep-tracking path)."""

        def clean_name(name):
            return (
                re.sub(r"[^a-zA-Z\s]", "", name).replace(" ", "_").lower()
                or "sn_module"
            )

        return f"{clean_name(self.name)}_{self.id}"

    def init(self):
        self.name = "Node Tree"
        self.id = get_short_id()
        self.use_fake_user = True
        self.initialized = True

    def update(self):
        if self.pause_updates:
            return
        self._mute_incompatible_links()
        self._remove_cyclic_links()
        self.update_links()
        self.update_node_references()
        bpy.app.timers.register(lambda: self.update_reroutes(), first_interval=0.001)

    def _mute_incompatible_links(self):
        """Mute links whose endpoints carry mismatched socket_type (DATA vs
        PROGRAM). Eval already filters these out via the socket helpers,
        but muting also gives the user a visual cue (Blender renders muted
        links dashed) so they see why their wiring didn't work.

        Handles two cases:
          1. Direct link between two SN sockets with mismatched types.
          2. Chain through reroutes - walk forward from each SN output and
             mute the final segment that lands on an SN socket of the
             wrong type. The reroute pass-through links stay unmuted so
             other (valid) branches off the same reroute keep working.
        """
        # 1. Direct SN-to-SN mismatches. Reroute-touching links get reset
        #    to unmuted here; the chain walk below re-mutes bad endpoints.
        for link in self.links:
            from_type = getattr(link.from_socket, "socket_type", None)
            to_type = getattr(link.to_socket, "socket_type", None)
            if from_type is not None and to_type is not None:
                should_mute = from_type != to_type
                if link.is_muted != should_mute:
                    link.is_muted = should_mute
            elif link.is_muted:
                link.is_muted = False

        # 2. Walk chains through reroutes from each SN output socket.
        for node in self.nodes:
            if node.bl_idname == "NodeReroute":
                continue
            for out in node.outputs:
                src_type = getattr(out, "socket_type", None)
                if src_type is None:
                    continue
                self._mute_chain_mismatches(out, src_type)

    def _mute_chain_mismatches(self, start_socket, src_type):
        """BFS through reroutes from `start_socket`, muting any link whose
        final SN target's socket_type doesn't match `src_type`."""
        visited = set()
        # Seed with links leaving start_socket
        queue = list(start_socket.links)
        while queue:
            link = queue.pop()
            to_node = link.to_node
            if to_node.bl_idname == "NodeReroute":
                key = to_node.as_pointer()
                if key in visited:
                    continue
                visited.add(key)
                queue.extend(to_node.outputs[0].links)
            else:
                target_type = getattr(link.to_socket, "socket_type", None)
                if target_type is not None and target_type != src_type:
                    if not link.is_muted:
                        link.is_muted = True

    def _remove_cyclic_links(self):
        """Strip any links that participate in a cycle. Logs each removal."""
        cyclic = [link for link in self.links if self._creates_cycle(link)]
        if not cyclic:
            return
        self.pause_updates = True
        try:
            for link in cyclic:
                log(
                    "WARNING",
                    f"Removed cyclic link: {link.from_node.name} -> {link.to_node.name}",
                )
                self.links.remove(link)
        finally:
            self.pause_updates = False

    def _creates_cycle(self, link):
        """True if from_node is reachable from to_node via downstream links."""
        target = link.from_node
        visited = set()
        stack = [link.to_node]
        while stack:
            node = stack.pop()
            if node is target:
                return True
            key = node.name
            if key in visited:
                continue
            visited.add(key)
            for out in node.outputs:
                for next_link in out.links:
                    stack.append(next_link.to_node)
        return False

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

    def update_node_references(self):
        # Safety check - ensure scene.sna is fully initialized
        if not hasattr(bpy.context.scene, "sna") or not hasattr(
            bpy.context.scene.sna, "references"
        ):
            return

        refs = bpy.context.scene.sna.references
        # Track ref names that changed - referencing nodes need to regenerate
        # so their code (e.g. cross-tree imports) reflects the new target id.
        affected_names = set()

        for node in sn_nodes(self):
            new_name = f"{node.name} ({self.name})"
            for ref in refs:
                if ref.node_id == node.id:
                    if ref.name != new_name:
                        affected_names.add(ref.name)
                        affected_names.add(new_name)
                        ref.name = new_name
                    break
            else:
                ref = refs.add()
                ref.name = new_name
                ref.node_id = node.id
                affected_names.add(new_name)

        # remove stale references (node deleted)
        for index in range(len(refs) - 1, -1, -1):
            ref = refs[index]
            if node_by_id(ref.node_id) is None:
                affected_names.add(ref.name)
                refs.remove(index)

        # Notify referencing nodes whose ref-property points to a changed name.
        if affected_names:
            for ntree in scripting_node_trees():
                for node in sn_nodes(ntree):
                    ref_props = getattr(node, "sn_reference_properties", set())
                    for prop in ref_props:
                        if getattr(node, prop, "") in affected_names:
                            node._generate()
                            break
                    # Container nodes hold refs in a CollectionProperty
                    cb_entries = getattr(node, "class_body_properties", None)
                    if cb_entries is not None:
                        for entry in cb_entries:
                            if entry.prop in affected_names:
                                node._generate()
                                break

    def update_reroutes(self):
        for node in self.nodes:
            if node.bl_idname == "NodeReroute":
                connected = from_socket(node.inputs[0])
                if connected and node.socket_idname != connected.bl_idname:
                    node.socket_idname = connected.bl_idname
                elif not connected and node.socket_idname != "ScriptingDataSocket":
                    node.socket_idname = "ScriptingDataSocket"
