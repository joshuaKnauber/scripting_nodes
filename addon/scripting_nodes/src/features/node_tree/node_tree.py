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

    is_dirty: bpy.props.BoolProperty(default=True)

    def update(self):
        self.update_links()

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
