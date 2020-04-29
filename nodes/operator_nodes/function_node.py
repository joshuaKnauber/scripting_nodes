import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ...utitlity_functions import to_lower_camelcase


class SN_FunctionNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for starting a function'''
    bl_idname = 'SN_FunctionNode'
    bl_label = "Function Start"
    bl_icon = node_icons["OPERATOR"]

    def update_function_name(self,context):
        if not self.updating_props:
            self.updating_props = True
            self.name = to_lower_camelcase(self.name)
            self.updating_props = False

    updating_props: bpy.props.BoolProperty(default=False)
    name: bpy.props.StringProperty(default="newFunction", update=update_function_name)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        #Node Outputs
        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"name",text="Name")

    def socket_value_update(self, context):
        print("socket update")

    def insert_link(self, link):
        pass

    def evaluate(self,output):
        next_node = None
        if len(self.outputs[0].links) > 0:
            next_node = self.outputs[0].links[0].to_node
        return {
                "code": [],
                "indented_blocks": [
                    {
                        "code": ["def " + self.name + "():\n"],
                        "function_node": next_node
                    }
                ]
                }