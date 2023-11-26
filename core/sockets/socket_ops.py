import bpy

from ..utils.nodes import get_node_by_id
from ..utils.sockets import add_socket


class SNA_OT_AddDynamicSocket(bpy.types.Operator):
    bl_idname = "sna.add_dynamic_socket"
    bl_label = "Add Dynamic Socket"

    node: bpy.props.StringProperty()
    is_output: bpy.props.BoolProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        row = self.layout.row(align=True)
        op = row.operator("sna.add_dynamic_socket_run", text="Above", icon="TRIA_UP")
        op.node = self.node
        op.is_output = self.is_output
        op.index = self.index
        op.above = True
        op = row.operator("sna.add_dynamic_socket_run", text="Below", icon="TRIA_DOWN")
        op.node = self.node
        op.is_output = self.is_output
        op.index = self.index
        op.above = False

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=150)


class SNA_OT_AddDynamicSocketRun(bpy.types.Operator):
    bl_idname = "sna.add_dynamic_socket_run"
    bl_label = "Add Dynamic Socket"

    node: bpy.props.StringProperty()
    is_output: bpy.props.BoolProperty()
    index: bpy.props.IntProperty()
    above: bpy.props.BoolProperty()

    def execute(self, context):
        node = get_node_by_id(self.node)
        if node:
            socket = (
                node.inputs[self.index]
                if not self.is_output
                else node.outputs[self.index]
            )
            new_socket = add_socket(node, socket.bl_idname, socket.name, self.is_output)
            new_socket.dynamic = True
            new_index = self.index if self.above else self.index + 1
            if self.is_output:
                node.outputs.move(len(node.outputs) - 1, new_index)
            else:
                node.inputs.move(len(node.inputs) - 1, new_index)
            node.mark_dirty()
        return {"FINISHED"}


class SNA_OT_RemoveSocket(bpy.types.Operator):
    bl_idname = "sna.remove_socket"
    bl_label = "Remove Socket"

    node: bpy.props.StringProperty()
    is_output: bpy.props.BoolProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        node = get_node_by_id(self.node)
        if node:
            socket = (
                node.inputs[self.index]
                if not self.is_output
                else node.outputs[self.index]
            )
            if self.is_output:
                node.outputs.remove(socket)
            else:
                node.inputs.remove(socket)
            node.mark_dirty()
        return {"FINISHED"}
