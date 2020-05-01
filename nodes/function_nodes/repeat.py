import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_RepeatNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Repeat node for repeating a task'''
    bl_idname = 'SN_RepeatNode'
    bl_label = "Repeat"
    bl_icon = node_icons["PROGRAM"]

    def register_sockets(self,context):
        for inp in self.inputs:
            self.inputs.remove(inp)
        for out in self.outputs:
            self.outputs.remove(out)

        if self.is_layout:
            socket_type = "SN_LayoutSocket"
            socket_name = "Layout"
            socket_shape = "CIRCLE"
        else:
            socket_type = "SN_ProgramSocket"
            socket_name = "Program"
            socket_shape = "DIAMOND"

        inp = self.inputs.new(socket_type, socket_name)
        inp.display_shape = socket_shape

        self.inputs.new('SN_NumberSocket', "Value").value = 2

        out = self.outputs.new(socket_type, socket_name)
        out.display_shape = socket_shape

        repeat = self.outputs.new(socket_type, "Repeat")
        repeat.display_shape = socket_shape

    is_layout: bpy.props.BoolProperty(default=False,update=register_sockets)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["PROGRAM"]

        self.register_sockets(context)

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass

    def draw_buttons(self, context, layout):
        pass

    def evaluate(self,output):
        value = str(self.inputs[1].value)

        if self.inputs[1].is_linked:
            value = self.inputs[1].links[0].from_socket

        repeat_next_node = None
        if self.outputs[1].is_linked:
            repeat_next_node = self.outputs[1].links[0].to_node

        return {
                "code": [],
                "indented_blocks": [
                    {
                        "code": ["for i in range(abs(int(", value, "))):\n"],
                        "function_node": repeat_next_node
                    }
                ]
                }
