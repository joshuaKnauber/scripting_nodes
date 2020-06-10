import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import get_input_value

class SN_RepeatNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Repeat node for repeating a task'''
    bl_idname = 'SN_RepeatNode'
    bl_label = "Repeat"
    bl_icon = node_icons["PROGRAM"]

    def register_sockets(self,context):
        self.inputs.clear()
        self.outputs.clear()

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

        self.inputs.new('SN_IntSocket', "Value").value = 2

        out = self.outputs.new(socket_type, socket_name)
        out.display_shape = socket_shape

        if self.is_layout:
            repeat = self.inputs.new(socket_type, "Repeat")
        else:
            repeat = self.outputs.new(socket_type, "Repeat")
        repeat.display_shape = socket_shape

        self.outputs.new("SN_IntSocket", "Step")

    def get_var_name(self):
        highest_var_name = 0
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname == self.bl_idname:
                number = int(node.var_name.split("_")[-1])
                highest_var_name = max(number,highest_var_name)
        return "i_"+str(highest_var_name + 1)

    is_layout: bpy.props.BoolProperty(default=False,update=register_sockets)

    var_name: bpy.props.StringProperty(default="i_0")

    def init(self, context):
        self.var_name = self.get_var_name()

        self.use_custom_color = True
        self.color = node_colors["PROGRAM"]

        self.register_sockets(context)

    def copy(self, node):
        self.var_name = self.get_var_name()

    def free(self):
        pass

    def draw_buttons(self, context, layout):
        pass

    def layout_type(self):
        return self.outputs[0].links[0].to_node.layout_type()

    def evaluate(self,output):
        value = str(self.inputs[1].value)
        errors = []

        if self.inputs[1].is_linked:
            value, error = get_input_value(self,"Value",["SN_IntSocket","SN_NumberSocket"])
            errors += error

        if output == self.outputs[-1]:
            return {"code":[self.var_name]}

        else:

            def_var = self.var_name + " = 0\n"

            if not self.is_layout:
                repeat_next_node = None
                if self.outputs[1].is_linked:
                    repeat_next_node = self.outputs[1].links[0].to_node

                return {
                        "code": [def_var],
                        "indented_blocks": [
                            {
                                "code": ["for ",self.var_name," in range(abs(int(", value, "))):\n"],
                                "function_node": repeat_next_node
                            }
                        ]
                        }

            else:
                layout = None
                if self.inputs[0].is_linked:
                    layout = [self.inputs[0].links[0].from_socket]

                repeat = "_MATCH_PREV__INDENT_pass\n"
                if self.inputs[2].is_linked:
                    repeat = self.inputs[2].links[0].from_socket

                functions = [
                    {
                        "socket": repeat,
                        "followup": layout
                    }
                ]

                def_var = "_INDENT__INDENT_" + def_var
                return {"code":[def_var,"_INDENT__INDENT_for ",self.var_name," in range(abs(int(", value, "))):\n"], "functions":functions,"error":errors}