import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_RepeatNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RepeatNode"
    bl_label = "Repeat (Program)"
    bl_icon = node_icons["PROGRAM"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def get_var_name(self):
        highest_var_name = 0
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname == self.bl_idname:
                number = int(node.var_name.split("_")[-1])
                highest_var_name = max(number,highest_var_name)
        return "repeat_"+str(highest_var_name + 1)

    var_name: bpy.props.StringProperty(default="repeat_0")

    def init(self, context):
        self.get_var_name()
        self.use_custom_color = True
        self.color = node_colors["PROGRAM"]
        
        inp = self.inputs.new('SN_ProgramSocket', "Program")
        inp.display_shape = "DIAMOND"

        self.inputs.new('SN_IntSocket', "Times").value = 2

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

        out = self.outputs.new('SN_ProgramSocket', "Repeat")
        out.display_shape = "DIAMOND"

        self.outputs.new("SN_IntSocket", "Step")

    def copy(self, node):
        self.get_var_name()

    def evaluate(self, output):
        if output == self.outputs[2]:
            return {
                "blocks": [
                    {
                        "lines": [
                            [self.var_name]
                        ],
                        "indented": [
                        ]
                    }
                ],
                "errors": []
            }
        else:
            value, errors = self.SocketHandler.socket_value(self.inputs[1])
            continue_code, error = self.SocketHandler.socket_value(self.outputs[0])
            errors+=error
            repeat_code, error = self.SocketHandler.socket_value(self.outputs[1])
            errors+=error
            if repeat_code == []:
                repeat_code = ["pass"]

            return {
                "blocks": [
                    {
                        "lines": [
                            ["for " + self.var_name + " in range("] + value + ["):"]
                        ],
                        "indented": [
                            repeat_code
                        ]
                    },
                    {
                        "lines": [
                            continue_code
                        ],
                        "indented": [
                        ]
                    }
                ],
                "errors": errors
            }


    def needed_imports(self):
        return []