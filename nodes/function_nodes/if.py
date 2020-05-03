import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_IfNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''If Node for spliting to do and else'''
    bl_idname = 'SN_IfNode'
    bl_label = "If"
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

        self.inputs.new('SN_BooleanSocket', "Value")

        out = self.outputs.new(socket_type, socket_name)
        out.display_shape = socket_shape

        if not self.is_layout:
            do = self.outputs.new(socket_type, "Do")
            do.display_shape = socket_shape
            els = self.outputs.new(socket_type, "Else")
            els.display_shape = socket_shape
        else:
            do = self.inputs.new(socket_type, "Do")
            do.display_shape = socket_shape
            els = self.inputs.new(socket_type, "Else")
            els.display_shape = socket_shape

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
        pass#layout.prop(self,"is_layout",text="Layout Node")

    def layout_type(self):
        return self.outputs[0].links[0].to_node.layout_type()

    def evaluate(self,output):
        value = str(self.inputs[1].value)

        if self.inputs[1].is_linked:
            value = self.inputs[1].links[0].from_socket

        if not self.is_layout:

            do_next_node = None
            if self.outputs[1].is_linked:
                do_next_node = self.outputs[1].links[0].to_node
            else_next_node = None
            if self.outputs[2].is_linked:
                else_next_node = self.outputs[2].links[0].to_node

            return {
                    "code": [],
                    "indented_blocks": [
                        {
                            "code": ["if ", value, ":\n"],
                            "function_node": do_next_node
                        },
                        {
                            "code": ["else:\n"],
                            "function_node": else_next_node
                        }
                    ]
                    }

        else:
            do_next_node = "_MATCH_PREV__INDENT_pass\n"
            if self.inputs[2].is_linked:
                do_next_node = self.inputs[2].links[0].from_socket
            else_next_node = "_MATCH_PREV__INDENT_pass\n"
            if self.inputs[3].is_linked:
                else_next_node = self.inputs[3].links[0].from_socket

            layout = None
            if self.inputs[0].is_linked:
                layout = [self.inputs[0].links[0].from_socket]

            functions = [
                {
                    "socket": do_next_node,
                    "followup": ["_KEEP_else:\n"]
                },
                {
                    "socket": else_next_node,
                    "followup": layout
                }
            ]

            return {"code":["_REMEMBER__INDENT__INDENT_if ",value,":\n"],"functions":functions}