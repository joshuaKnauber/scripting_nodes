import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_RandomNumberNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RandomNumberNode"
    bl_label = "Random Number"
    node_color = "FLOAT"

    def on_create(self, context):
        self.add_float_input("Minimum")
        self.add_float_input("Maximum")
        self.add_integer_output("Random Number")

    def update_num_type(self, context):
        self.convert_socket(self.outputs[0], self.socket_names[self.number_type])
        self._evaluate(context)
        
    number_type: bpy.props.EnumProperty(name="Type",
                                    description="Type of number",
                                    items=[("Integer", "Integer", "Integer"),
                                           ("Float", "Float", "Float")],
                                    update=update_num_type)

    def evaluate(self, context):
        if self.number_type == "Integer":
            self.code_import = "from random import randint"
            self.outputs[0].python_value = f"randint(int({self.inputs['Minimum'].python_value}), int({self.inputs['Maximum'].python_value}))"
        else:
            self.code_import = "from random import uniform"
            self.outputs[0].python_value = f"uniform({self.inputs['Minimum'].python_value}, {self.inputs['Maximum'].python_value})"

    def draw_node(self, context, layout):
        layout.prop(self, "number_type")