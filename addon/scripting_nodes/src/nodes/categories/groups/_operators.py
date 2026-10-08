"""New Group, Make Group (Ctrl+G) and Ungroup (Ctrl+Alt+G).

Blender's own group operators only run in its built-in node trees, so these
do the same for ours. Nodes move between trees through the node clipboard
(copy, paste), which keeps every node setting, frames and links between the
moved nodes. The clipboard's previous content is lost.
"""

import bpy

from ....core import functions, scheduler
from ....lib.is_sn import is_sn
from ....sockets.socket_types import FLOW_SOCKET
from ....sockets.interface import SOCKET_IDNAMES

IO = (functions.GROUP_INPUT, functions.GROUP_OUTPUT)
# marks nodes while they're moved, to find them after pasting
TAG = "sn_moved_from"


def _sn_editor(context):
    space = context.space_data
    return (
        space is not None
        and space.type == "NODE_EDITOR"
        and space.tree_type == "ScriptingNodeTree"
        and space.edit_tree is not None
    )


def _socket(node, identifier, output):
    sockets = node.outputs if output else node.inputs
    return next((s for s in sockets if s.identifier == identifier), None)


def _new_item(tree, socket, in_out):
    """Interface socket like `socket` (the socket inside the group)."""
    idname = socket.bl_idname if socket.bl_idname in SOCKET_IDNAMES else None
    item = tree.interface.new_socket(
        socket.name or "Value",
        in_out=in_out,
        socket_type=idname or "ScriptingDataSocket",
    )
    if idname == FLOW_SOCKET:
        item.kind = socket.kind
    for name in ("dimension", "use_alpha"):
        if hasattr(item, name) and hasattr(socket, name):
            setattr(item, name, getattr(socket, name))
    return item


def _center(nodes):
    xs = [node.location.x for node in nodes]
    ys = [node.location.y for node in nodes]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(xs), max(xs)


def new_function_tree(name, flow=True):
    """A function tree with Group Input / Output (and a flow through it)."""
    tree = bpy.data.node_groups.new(name, "ScriptingNodeTree")
    group_input = tree.nodes.new(functions.GROUP_INPUT)
    group_input.location = (-250, 0)
    group_output = tree.nodes.new(functions.GROUP_OUTPUT)
    group_output.location = (250, 0)
    if flow:
        tree.interface.new_socket("Run", in_out="INPUT", socket_type=FLOW_SOCKET)
        tree.interface.new_socket("Next", in_out="OUTPUT", socket_type=FLOW_SOCKET)
        tree.links.new(group_input.outputs[0], group_output.inputs[0])
    scheduler.request_full()
    return tree


class SNA_OT_NewGroup(bpy.types.Operator):
    """Create a function (node group) with Group Input and Group Output"""

    bl_idname = "sna.new_group"
    bl_label = "New Function"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        tree = new_function_tree("Function")
        node = getattr(context, "node", None) or getattr(context, "active_node", None)
        if node is not None and node.bl_idname == "SNA_Node_Group":
            node.node_tree = tree
        return {"FINISHED"}


class SNA_OT_MakeGroup(bpy.types.Operator):
    """Move the selected nodes into a new function and call it from here"""

    bl_idname = "sna.make_group"
    bl_label = "Make Group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return _sn_editor(context) and any(
            node.select and node.bl_idname not in IO
            for node in context.space_data.edit_tree.nodes
        )

    def execute(self, context):
        space = context.space_data
        parent = space.edit_tree
        selected = [n for n in parent.nodes if n.select and n.bl_idname not in IO]
        names = {node.name for node in selected}
        ids = {node.name: node.id for node in selected if is_sn(node)}
        # (node name, socket identifier) pairs, sockets change when nodes do
        inward = [
            (l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket)
            for l in parent.links
            if l.to_node.name in names and l.from_node.name not in names
        ]
        outward = [
            (l.from_node.name, l.from_socket, l.to_node.name, l.to_socket.identifier)
            for l in parent.links
            if l.from_node.name in names and l.to_node.name not in names
        ]
        x, y, left, right = _center(selected)

        for node in parent.nodes:
            node.select = node.name in names
        bpy.ops.node.clipboard_copy()

        group = bpy.data.node_groups.new("Group", "ScriptingNodeTree")
        # one parameter per outside socket, one return value per inside socket
        inputs, outputs = {}, {}
        for from_name, from_id, _, to_socket in inward:
            if (from_name, from_id) not in inputs:
                inputs[(from_name, from_id)] = _new_item(group, to_socket, "INPUT")
        for from_name, from_socket, _, _ in outward:
            key = (from_name, from_socket.identifier)
            if key not in outputs:
                outputs[key] = _new_item(group, from_socket, "OUTPUT")
        inward = [(f, i, t, s.identifier) for f, i, t, s in inward]
        outward = [(f, s.identifier, t, i) for f, s, t, i in outward]

        call = parent.nodes.new("SNA_Node_Group")
        call.location = (x, y)
        call.node_tree = group
        call.sync_sockets()

        space.path.append(group, node=call)
        bpy.ops.node.clipboard_paste()
        group_input = group.nodes.new(functions.GROUP_INPUT)
        group_input.location = (left - 250, y)
        group_output = group.nodes.new(functions.GROUP_OUTPUT)
        group_output.location = (right + 250, y)

        for from_name, from_id, to_name, to_id in inward:
            identifier = inputs[(from_name, from_id)].identifier
            group.links.new(
                _socket(group_input, identifier, True),
                _socket(group.nodes[to_name], to_id, False),
            )
            parent.links.new(
                _socket(parent.nodes[from_name], from_id, True),
                _socket(call, identifier, False),
            )
        for from_name, from_id, to_name, to_id in outward:
            identifier = outputs[(from_name, from_id)].identifier
            group.links.new(
                _socket(group.nodes[from_name], from_id, True),
                _socket(group_output, identifier, False),
            )
            parent.links.new(
                _socket(call, identifier, True),
                _socket(parent.nodes[to_name], to_id, False),
            )

        for node in selected:
            parent.nodes.remove(node)
        # the moved nodes keep their ids, so references to them still work
        for name, node_id in ids.items():
            group.nodes[name].id = node_id
        scheduler.request_full()
        return {"FINISHED"}


class SNA_OT_Ungroup(bpy.types.Operator):
    """Put the nodes of the selected group nodes back into this tree"""

    bl_idname = "sna.ungroup"
    bl_label = "Ungroup"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return _sn_editor(context) and any(
            node.select and node.bl_idname == "SNA_Node_Group" and node.node_tree
            for node in context.space_data.edit_tree.nodes
        )

    def execute(self, context):
        space = context.space_data
        parent = space.edit_tree
        calls = [
            node
            for node in parent.nodes
            if node.select and node.bl_idname == "SNA_Node_Group" and node.node_tree
        ]
        for call in calls:
            self.ungroup(space, parent, call)
        scheduler.request_full()
        return {"FINISHED"}

    def ungroup(self, space, parent, call):
        group = call.node_tree
        inner = [node for node in group.nodes if node.bl_idname not in IO]
        # links of the interface inside the group: item identifier -> sockets
        params, returns, through = {}, {}, {}
        for link in group.links:
            from_io = link.from_node.bl_idname == functions.GROUP_INPUT
            to_io = link.to_node.bl_idname == functions.GROUP_OUTPUT
            if from_io and to_io:
                through.setdefault(link.from_socket.identifier, []).append(
                    link.to_socket.identifier
                )
            elif from_io:
                params.setdefault(link.from_socket.identifier, []).append(
                    (link.to_node.name, link.to_socket.identifier)
                )
            elif to_io:
                returns[link.to_socket.identifier] = (
                    link.from_node.name,
                    link.from_socket.identifier,
                )
        # outside: call socket identifier -> sockets
        sources = {
            l.to_socket.identifier: l.from_socket
            for l in parent.links
            if l.to_node == call
        }
        targets = {}
        for link in parent.links:
            if link.from_node == call:
                targets.setdefault(link.from_socket.identifier, []).append(
                    link.to_socket
                )
        values = {
            s.identifier: s.value
            for s in call.inputs
            if not s.is_linked and hasattr(s, "value")
        }

        pasted = {}
        if inner:
            x, y, _, _ = _center(inner)
            for node in group.nodes:
                node.select = node in inner
                if node in inner:
                    node[TAG] = node.name
            space.path.append(group, node=call)
            bpy.ops.node.clipboard_copy()
            space.path.pop()
            for node in inner:
                del node[TAG]
            for node in parent.nodes:
                node.select = False
            bpy.ops.node.clipboard_paste()
            for node in parent.nodes:
                if node.get(TAG) is not None:
                    pasted[node[TAG]] = node
                    del node[TAG]
                    if node.parent is None:
                        node.location.x += call.location.x - x
                        node.location.y += call.location.y - y

        for identifier, uses in params.items():
            for name, socket_id in uses:
                target = _socket(pasted[name], socket_id, False)
                if identifier in sources:
                    parent.links.new(sources[identifier], target)
                elif identifier in values and hasattr(target, "value"):
                    try:
                        target.value = values[identifier]
                    except (TypeError, ValueError):
                        pass
        for identifier, (name, socket_id) in returns.items():
            source = _socket(pasted[name], socket_id, True)
            for target in targets.get(identifier, ()):
                parent.links.new(source, target)
        for identifier, outputs in through.items():
            if identifier not in sources:
                continue
            for output in outputs:
                for target in targets.get(output, ()):
                    parent.links.new(sources[identifier], target)
        parent.nodes.remove(call)
