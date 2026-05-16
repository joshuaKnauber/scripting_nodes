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
