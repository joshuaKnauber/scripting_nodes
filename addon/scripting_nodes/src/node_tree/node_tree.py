from collections import defaultdict

import bpy

from ..core import functions, naming, scheduler
from ..core.versioning import DATA_VERSION
from ..lib.ids import get_short_id
from ..lib.logger import log
from ..lib.sockets import from_socket
from ..lib.trees import sn_nodes
from ..sockets.interface import SOCKET_IDNAMES


# False until every class is registered and again during unregister. Blender
# calls NodeTree.update() on existing trees while node/socket classes are
# (un)registered one by one; touching them in that window crashes Blender.
_READY = False


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
    # Version of the saved data layout, see core/versioning.py
    data_version: bpy.props.IntProperty(default=0)
    pause_updates: bpy.props.BoolProperty(default=False)

    @classmethod
    def valid_socket_type(cls, idname):
        """Socket types offered in the group interface (sidebar "Group" tab)."""
        return idname in SOCKET_IDNAMES

    @property
    def is_function(self):
        """Has a group interface: compiles to a function, see core/functions."""
        return functions.is_function(self)

    @property
    def module_name(self):
        """Python module of this tree, e.g. `main` (core/naming.py)."""
        return naming.name(self, "module")

    @property
    def function_name(self):
        """Function a tree with a group interface defines, e.g. `greet`."""
        return naming.name(self, "function")

    def init(self):
        self.id = get_short_id()
        self.data_version = DATA_VERSION
        self.use_fake_user = True
        self.initialized = True

    def update(self):
        if not _READY or self.pause_updates:
            return
        self._remove_cyclic_links(list(self.links))
        self._mute_incompatible_links(list(self.links))
        for node in sn_nodes(self):
            node.update_dynamic_sockets()
        # Links or nodes changed: regenerate this tree on the next flush
        scheduler.request_tree(self)

    def _mute_incompatible_links(self, links):
        """Mute links that connect a DATA socket with a PROGRAM socket.

        Eval already ignores these, muting gives the user a visual cue
        (dashed link). Through reroutes, only the final segment landing on
        an incompatible SN socket is muted, so other branches off the same
        reroute keep working. Linear in the number of links.
        """
        reroute_out = defaultdict(list)  # reroute name -> links leaving it
        for link in links:
            if link.from_node.bl_idname == "NodeReroute":
                reroute_out[link.from_node.name].append(link)

        mute = set()
        for link in links:
            src_type = getattr(link.from_socket, "socket_type", None)
            if src_type is None:
                continue  # starts at a reroute or non-SN node
            # follow the link (and reroute chains) to SN targets
            stack, seen = [link], set()
            while stack:
                current = stack.pop()
                to_node = current.to_node
                if to_node.bl_idname == "NodeReroute":
                    if to_node.name not in seen:
                        seen.add(to_node.name)
                        stack.extend(reroute_out[to_node.name])
                    continue
                to_type = getattr(current.to_socket, "socket_type", None)
                if to_type is not None and to_type != src_type:
                    mute.add(current.as_pointer())

        for link in links:
            should_mute = link.as_pointer() in mute
            if link.is_muted != should_mute:
                link.is_muted = should_mute

    def _remove_cyclic_links(self, links):
        """Remove links that are part of a cycle (strongly connected component
        with more than one node, or a self-loop). Linear in links + nodes."""
        graph = defaultdict(list)
        for link in links:
            graph[link.from_node.name].append(link.to_node.name)
        component = _strongly_connected_components(graph)
        cyclic = [
            link
            for link in links
            if component.get(link.from_node.name) is not None
            and component.get(link.from_node.name) == component.get(link.to_node.name)
        ]
        if not cyclic:
            return False
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
        return True

    def update_reroutes(self):
        for node in self.nodes:
            if node.bl_idname == "NodeReroute":
                connected = from_socket(node.inputs[0])
                if connected and node.socket_idname != connected.bl_idname:
                    node.socket_idname = connected.bl_idname
                elif not connected and node.socket_idname != "ScriptingDataSocket":
                    node.socket_idname = "ScriptingDataSocket"


def _strongly_connected_components(graph):
    """{node: component id} for nodes on a cycle (iterative Tarjan).

    Nodes not on any cycle are left out. `graph` maps node -> successors."""
    index, low, on_stack, stack = {}, {}, set(), []
    result, counter = {}, [0]
    for root in list(graph):
        if root in index:
            continue
        work = [(root, iter(graph.get(root, ())))]
        index[root] = low[root] = counter[0]
        counter[0] += 1
        stack.append(root)
        on_stack.add(root)
        while work:
            node, successors = work[-1]
            for succ in successors:
                if succ not in index:
                    index[succ] = low[succ] = counter[0]
                    counter[0] += 1
                    stack.append(succ)
                    on_stack.add(succ)
                    work.append((succ, iter(graph.get(succ, ()))))
                    break
                if succ in on_stack:
                    low[node] = min(low[node], index[succ])
            else:
                work.pop()
                if work:
                    parent = work[-1][0]
                    low[parent] = min(low[parent], low[node])
                if low[node] == index[node]:
                    members = []
                    while True:
                        member = stack.pop()
                        on_stack.discard(member)
                        members.append(member)
                        if member == node:
                            break
                    if len(members) > 1 or node in graph.get(node, ()):
                        for member in members:
                            result[member] = node
    return result


def register():
    global _READY
    _READY = True


def unregister():
    global _READY
    _READY = False
