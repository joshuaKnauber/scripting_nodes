import bpy
from ..use_operator import SN_UseOperatorNode
from ..node_looks import node_colors, node_icons
from ...node_sockets import update_socket_autocompile


class SN_OperatorRunNode(bpy.types.Node, SN_UseOperatorNode):
    '''Node for running an operator'''
    bl_idname = 'SN_OperatorRunNode'
    bl_label = "Run Operator"
    bl_icon = node_icons["OPERATOR"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        inp = self.inputs.new('SN_ProgramSocket', "Program")
        inp.display_shape = "DIAMOND"

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

        self.generate_sockets()
        self.op_items()

    def draw_buttons(self, context, layout):
        layout.prop_search(self,"opType",context.scene,"sn_op_type_properties",text="")
        if self.opType != "":
            layout.prop_search(self,"opRun",context.scene,"sn_op_run_properties",text="")

    def evaluate(self,output):
        opType = self.opType.lower().replace(" ","_")
        opRun = self.opRun.lower().replace(" ","_")
        props = ""
        for inp in self.inputs:
            if not inp.bl_idname == "SN_ProgramSocket":
                value = inp.value
                if type(value) == str:
                    value = "'" + value + "'"
                elif inp.bl_idname == "SN_VectorSocket":
                    tuple_value = value
                    value = "("
                    for entry in tuple_value:
                        value += str(entry) + ","
                    value += ")"
                else:
                    value = str(value)
                props += inp.name.lower().replace(" ","_") + "=" + value + ", "
        return {"code": ["bpy.ops."+opType+"."+opRun+"("+props+")\n"]}