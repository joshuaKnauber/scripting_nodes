from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_List(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_List"
    bl_label = "List"

    last_connected_from_node: bpy.props.StringProperty(default="")
    last_connected_from_socket: bpy.props.StringProperty(default="")

    def on_create(self):
        inp = self.add_input("ScriptingDataSocket", "List Item")
        inp.is_dynamic = True
        dynamic = self.add_input("ScriptingDynamicAddInputSocket", "Add Input")
        dynamic.add_socket_type = "ScriptingDataSocket"
        dynamic.add_socket_name = "List Item"
        self.add_output("ScriptingListSocket", "List")

    def on_socket_added(self, socket):
        add_idx = -1
        for i, s in enumerate(self.inputs):
            if s.bl_idname == "ScriptingDynamicAddInputSocket":
                add_idx = i
                break

        if add_idx >= 0 and add_idx < len(self.inputs) - 1:
            self.inputs.move(add_idx, len(self.inputs) - 1)

        socket.is_dynamic = True

    def ntree_link_created(self):
        dynamic_socket = next(
            (s for s in self.inputs if s.bl_idname == "ScriptingDynamicAddInputSocket"),
            None,
        )

        if not dynamic_socket or not dynamic_socket.links:
            return

        link = dynamic_socket.links[0]
        self.last_connected_from_node = link.from_node.name
        self.last_connected_from_socket = link.from_socket.name

        self.id_data.links.remove(link)

        inp = self.add_input(
            dynamic_socket.add_socket_type, dynamic_socket.add_socket_name
        )
        inp.is_dynamic = True

        add_idx = -1
        for i, s in enumerate(self.inputs):
            if s.bl_idname == "ScriptingDynamicAddInputSocket":
                add_idx = i
                break

        if add_idx >= 0 and add_idx < len(self.inputs) - 1:
            self.inputs.move(add_idx, len(self.inputs) - 1)

        last_socket = self.inputs[-2] if len(self.inputs) >= 2 else None

        if last_socket:
            from_node = self.id_data.nodes.get(self.last_connected_from_node)
            if from_node:
                from_socket = next(
                    (
                        s
                        for s in from_node.outputs
                        if s.name == self.last_connected_from_socket
                    ),
                    None,
                )
                if from_socket:
                    self.id_data.links.new(from_socket, last_socket)

    def generate(self):
        items = []
        for i, socket in enumerate(self.inputs):
            if (
                socket.bl_idname != "ScriptingDynamicAddInputSocket"
                and socket.is_linked
            ):
                items.append(socket.eval())

        items_str = ", ".join(items)
        self.outputs[0].code = f"[{items_str}]"
