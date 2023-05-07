import bpy
from .queue import add_to_queue
import functools


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

    def _update_removed_links(self, removed_links):
        """ Trigger the callback on the nodes of the removed links. """
        for from_socket, to_socket in removed_links:
            if from_socket.node:
                from_socket.node.remove_link(
                    from_socket, to_socket if to_socket.node else None)
            if to_socket.node:
                to_socket.node.remove_link(
                    from_socket if from_socket.node else None, to_socket)

    def _validate_links(self):
        """ Validate new links """
        for link in self.links:
            if link.from_socket.is_program != link.to_socket.is_program:
                link.is_valid = False
            elif link.from_socket.is_program and not link == link.from_socket.links[0]:
                link.is_valid = False
            else:
                link.is_valid = True

    def _update_links(self):
        current_links = set(
            map(lambda l: (l.from_socket, l.to_socket), self.links))

        self._update_removed_links(self._previous_links - current_links)
        self._previous_links = current_links

        bpy.app.timers.register(self._validate_links, first_interval=0.0001)

    def update(self):
        """ Update the node tree. """
        self._update_links()
