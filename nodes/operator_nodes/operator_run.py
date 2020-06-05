import bpy
from ..function_nodes.use_operator import SN_UseOperatorNode
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
        layout.label(text=self.opDescription)

    def evaluate(self,output):
        opType = self.get_identifier()
        props = []
        for inp in self.inputs:
            if not inp.bl_idname == "SN_ProgramSocket":
                if not inp.is_linked:
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
                    props.append([inp.name.lower().replace(" ","_") + "=" + value + ", "])
                else:
                    props.append([inp.name.lower().replace(" ","_") + "=", inp.links[0].from_socket, ", "])
        
        allProps = []
        for prop in props:
            allProps+=prop
        
        return {"code": [opType, "("] + allProps + [")\n"]}
