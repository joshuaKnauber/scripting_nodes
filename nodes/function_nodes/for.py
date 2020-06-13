import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import get_input_value
from ..input_nodes.scene_nodes_utils import get_bpy_types

class SN_ForNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''For Node for running functions for every element'''
    bl_idname = 'SN_ForNode'
    bl_label = "For"
    bl_icon = node_icons["PROGRAM"]

    def get_var_name(self):
        highest_var_name = 0
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname == self.bl_idname:
                number = int(node.var_name.split("_")[-1])
                highest_var_name = max(number,highest_var_name)
        return "i_"+str(highest_var_name + 1)

    var_name: bpy.props.StringProperty(default="i_0")

    def init(self, context):
        self.var_name = self.get_var_name()
        self.use_custom_color = True
        self.color = node_colors["PROGRAM"]

        inp = self.inputs.new('SN_ProgramSocket', "Program")
        inp.display_shape = "DIAMOND"

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

        out = self.outputs.new('SN_ProgramSocket', "Repeat")
        out.display_shape = "DIAMOND"

        out = self.outputs.new('SN_SceneDataSocket', "Element")
        out.display_shape = "SQUARE"

        inp = self.inputs.new('SN_SceneDataSocket', "Scene Data")
        inp.display_shape = "SQUARE"

    def copy(self, node):
        self.var_name = self.get_var_name()

    def free(self):
        pass

    def draw_buttons(self, context, layout):
        pass

    def internal_evaluate( self, output ):
        if self.inputs[1].is_linked:
            if self.inputs[1].bl_idname == "SN_SceneDataSocket":
                if output == self.outputs[2]:
                    _, code = self.test_for_collection(False)
                    if code != []:
                        if "bl_rna.properties" in code[0]:
                            code = eval("type("+code[0]+".fixed_type)").bl_rna.identifier
                            code = "bpy.types." + code
                            return {"code": code}
                        else:
                            code = code[0].split(".")
                            types = get_bpy_types()[code[-1]]
                            return {"code": ["bpy.types." + types]}
                    else:
                        return {"code": [""]}
                else:
                    return {"code": [""]}
            else:
                return {"code": [""]}
        else:
            return {"code": [""]}


    def test_for_collection( self, use_evaluate ):
        errors = []
        value = []
        if self.inputs[1].links[0].from_node.bl_idname == "SN_DataPropertiesNode" and self.inputs[1].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
            if use_evaluate:
                code = ("").join(self.inputs[1].links[0].from_node.evaluate(self.inputs[1].links[0].from_socket)["code"])
            else:
                code = ("").join(self.inputs[1].links[0].from_node.internal_evaluate(self.inputs[1].links[0].from_socket)["code"])
                try:
                    if str(type(eval(code))) == "<class 'bpy_prop_collection'>":
                        value = [code]
                except KeyError:
                    errors.append("wrong_socket")


        elif self.inputs[1].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
            if use_evaluate:
                value = [("").join(self.inputs[1].links[0].from_node.evaluate(self.inputs[1].links[0].from_socket)["code"])]
            else:
                code = ("").join(self.inputs[1].links[0].from_node.internal_evaluate(self.inputs[1].links[0].from_socket)["code"])
                try:
                    if str(type(eval(code))) == "<class 'bpy_prop_collection'>":
                        value = [code]
                except KeyError:
                    errors.append("wrong_socket")
        else:
            errors.append("wrong_socket")
        return errors, value

    def evaluate(self, output):
        if output == self.outputs[-1]:
            return {"code":[self.var_name]}

        errors = []

        value = ["[]"]
        if self.inputs[1].is_linked:
            error, value = self.test_for_collection(True)
            errors += error
            if value == []:
                errors.append("wrong_socket")
        else:
            errors.append("no_connection_for")


        defVar = self.var_name + " = 0\n"
        do_next_node = None
        if self.outputs[1].is_linked:
            do_next_node = self.outputs[1].links[0].to_node

        return {
                "code": [defVar],
                "indented_blocks": [
                    {
                        "code": ["for " + self.var_name + " in "] + value + [":\n"],
                        "function_node": do_next_node
                    }
                ],
                "error": errors
                }
