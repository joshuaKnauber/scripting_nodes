import bpy
from .queue import add_to_queue


class ScriptingNodesTree(bpy.types.NodeTree):
    bl_idname = "ScriptingNodesTree"
    bl_label = "Visual Scripting Editor"
    bl_icon = "FILE_SCRIPT"
    is_sn = True
    type: bpy.props.EnumProperty(
        items=[("SCRIPTING", "Scripting", "Scripting")], name="Type"
    )

    def add_to_queue(self, node):
        """ Adds the given node to the queue for processing. """
        add_to_queue(node)

    _previous_links = set()

    def _trigger_removed_links(self):
        """ Trigger the callback on the nodes of the removed links. """
        current_links = set(
            map(lambda l: (l.from_socket, l.to_socket), self.links))
        for from_socket, to_socket in self._previous_links - current_links:
            if from_socket.node:
                from_socket.node.remove_link(
                    from_socket, to_socket if to_socket.node else None)
            if to_socket.node:
                to_socket.node.remove_link(
                    from_socket if from_socket.node else None, to_socket)
        self._previous_links = current_links

    def update(self):
        """ Update the node tree. """
        self._trigger_removed_links()
