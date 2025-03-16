import bpy


class SNA_OT_AddSocket(bpy.types.Operator):
    bl_idname = "sna.add_socket"
    bl_label = "Add Socket"
    bl_description = "Add a new input socket to this node"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_name: bpy.props.StringProperty()
    tree_name: bpy.props.StringProperty()
    socket_type: bpy.props.StringProperty(default="ScriptingDataSocket")
    socket_name: bpy.props.StringProperty(default="Item")

    def execute(self, context):
        try:
            tree = bpy.data.node_groups[self.tree_name]
            node = tree.nodes[self.node_name]

            new_socket = node.add_input(self.socket_type, self.socket_name)

            if hasattr(node, "on_socket_added"):
                node.on_socket_added(new_socket)

            node._generate()

            return {"FINISHED"}
        except (KeyError, AttributeError) as e:
            self.report({"ERROR"}, f"Could not add socket: {str(e)}")
            return {"CANCELLED"}


class SNA_OT_RemoveSocket(bpy.types.Operator):
    bl_idname = "sna.remove_socket"
    bl_label = "Remove Socket"
    bl_description = "Remove this socket from the node"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_name: bpy.props.StringProperty()
    tree_name: bpy.props.StringProperty()
    socket_index: bpy.props.IntProperty()

    def execute(self, context):
        try:
            tree = bpy.data.node_groups[self.tree_name]
            node = tree.nodes[self.node_name]

            if (
                self.socket_index < len(node.inputs)
                and node.inputs[self.socket_index].bl_idname
                != "ScriptingDynamicAddInputSocket"
            ):

                node.inputs.remove(node.inputs[self.socket_index])
                node._generate()

            return {"FINISHED"}
        except (KeyError, AttributeError) as e:
            self.report({"ERROR"}, f"Could not remove socket: {str(e)}")
            return {"CANCELLED"}
