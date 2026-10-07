import bpy

from ...lib.trees import node_by_id


class SNA_OT_AddDynamicSocket(bpy.types.Operator):
    bl_idname = "sna.add_dynamic_socket"
    bl_label = "Add Socket"
    bl_description = "Add another socket to this group"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    is_output: bpy.props.BoolProperty()
    socket_identifier: bpy.props.StringProperty()

    def execute(self, context):
        node = node_by_id(self.node_id)
        if node is None:
            return {"CANCELLED"}
        node.add_dynamic_socket(self.socket_identifier, self.is_output)
        return {"FINISHED"}


class SNA_OT_RemoveDynamicSocket(bpy.types.Operator):
    bl_idname = "sna.remove_dynamic_socket"
    bl_label = "Remove Socket"
    bl_description = "Remove this socket"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    is_output: bpy.props.BoolProperty()
    socket_index: bpy.props.IntProperty()

    def execute(self, context):
        node = node_by_id(self.node_id)
        if node is None:
            return {"CANCELLED"}
        sockets = node.outputs if self.is_output else node.inputs
        if 0 <= self.socket_index < len(sockets):
            sockets.remove(sockets[self.socket_index])
        node.mark_dirty()
        return {"FINISHED"}
