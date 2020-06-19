import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_ForNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ForNode"
    bl_label = "For"
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
        return "forNode_"+str(highest_var_name + 1)

    var_name: bpy.props.StringProperty(default="forNode_0")
    is_collection: bpy.props.BoolProperty()

    def init(self, context):
        self.var_name = self.get_var_name()
        self.use_custom_color = True
        self.color = node_colors["PROGRAM"]
        
        inp = self.inputs.new('SN_ProgramSocket', "Program")
        inp.display_shape = "DIAMOND"

        inp = self.inputs.new('SN_SceneDataSocket', "Scene Data")
        inp.display_shape = "SQUARE"

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

        out = self.outputs.new('SN_ProgramSocket', "Repeat")
        out.display_shape = "DIAMOND"

        out = self.outputs.new('SN_SceneDataSocket', "Element")
        out.display_shape = "SQUARE"

    def copy(self, node):
        self.var_name = self.get_var_name()

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

    def evaluate(self, output):
        self.test_collection()
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
        
        elif output == self.outputs[0]:
            continue_code, errors = self.SocketHandler.socket_value(self.outputs[0], False)
            return {
                "blocks": [
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
            for_code, errors = self.SocketHandler.socket_value(self.inputs[1])
            if self.is_collection == False:
                for_code = ["["] + for_code + ["]"]
            repeat_code, error = self.SocketHandler.socket_value(self.outputs[1], False)
            errors+=error
            continue_code, error = self.SocketHandler.socket_value(self.outputs[0], False)
            errors+=error
            if repeat_code == []:
                repeat_code = ["pass"]

            return {
                "blocks": [
                    {
                        "lines": [
                            [self.var_name + " = 0"],
                            ["for " + self.var_name + " in "] + for_code + [":"]
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

    def data_type(self, output):
        self.test_collection()
        if self.is_collection:
            code = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
            if "bpy.data" in code:
                code = code.split(".")[-1]
                code = "bpy.data.bl_rna.properties['" + code + "']"
                print("bpy.types." + eval("type(" + code + ".fixed_type)").bl_rna.identifier)
            return "bpy.types." + eval("type(" + code + ".fixed_type)").bl_rna.identifier
        else:
            return ""

    def needed_imports(self):
        return []