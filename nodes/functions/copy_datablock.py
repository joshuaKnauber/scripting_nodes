import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_CopyData(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CopyData"
    bl_label = "Copy Scene Data"
    bl_icon = node_icons["OPERATOR"]

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
        return "copyDatablockNode_"+str(highest_var_name + 1)

    def test_collection(self):
        if len(self.inputs[1].links) > 0:
            if self.inputs[1].links[0].from_node.bl_idname == "SN_SceneData":
                self.is_collection = True
            elif self.inputs[1].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                code = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
                if code != "":
                    if "bl_rna.properties" in code:
                        if eval(code).type == "COLLECTION":
                            self.is_collection = True
                        else:
                            self.is_collection = False
                    else:
                        self.is_collection = False
                else:
                    self.is_collection = False
            else:
                self.is_collection = False

    var_name: bpy.props.StringProperty(default="copyDatablockNode_0")
    is_collection: bpy.props.BoolProperty()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]
        
        self.inputs.new('SN_ProgramSocket', "Program").display_shape = "DIAMOND"
        self.inputs.new('SN_SceneDataSocket', 'Scene Data').display_shape = "SQUARE"

        self.outputs.new('SN_ProgramSocket', "Program").display_shape = "DIAMOND"
        self.outputs.new('SN_SceneDataSocket', 'Scene Data').display_shape = "SQUARE"

    def copy(self, node):
        self.var_name = self.get_var_name()

    def evaluate(self, output):
        if output == self.outputs[1]:
            return {
                "blocks": [
                    {
                        "lines": [
                            [self.var_name]
                        ],
                        "indented": []
                    }
                ],
                "errors": []
            }
        
        else:
            self.test_collection()
            if not self.is_collection:
                data, errors = self.SocketHandler.socket_value(self.inputs[1])
                continue_code, error = self.SocketHandler.socket_value(self.outputs[0], False)
                errors+=error
                return {
                    "blocks": [
                        {
                            "lines": [
                                [self.var_name + " = "] + data + [".copy()"]
                            ],
                            "indented": []
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
            else:
                return {
                    "blocks": [
                        {
                            "lines": [
                                [self.var_name + " = 0"]
                            ],
                            "indented": []
                        }
                    ],
                    "errors": [{"error": "wrong_socket_inp", "node": self}]
                }
        
    def data_type(self, output):
        self.test_collection()
        if not self.is_collection:
            code = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
            return code
        else:
            return ""

    def needed_imports(self):
        return []

