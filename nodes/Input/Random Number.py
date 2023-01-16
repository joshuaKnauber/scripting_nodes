import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_RandomNumberNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_RandomNumberNode"
    bl_label = "Random Number"
    node_color = "FLOAT"

    def on_create(self, context):
        self.add_float_input("Minimum")
        self.add_float_input("Maximum")
        inp = self.add_integer_input("Seed")
        inp.can_be_disabled = True
        inp.disabled = True
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
        self.code_import = "import random"
        if "Seed" in self.inputs and not self.inputs["Seed"].disabled:
            self.code_imperative = """
            def random_integer(min, max, seed):
                random.seed(seed)
                return random.randint(int(min), int(max))

            def random_float(min, max, seed):
                random.seed(seed)
                return random.uniform(min, max)
            """
            if self.number_type == "Integer":
                self.outputs[0].python_value = f"random_integer({self.inputs['Minimum'].python_value}, {self.inputs['Maximum'].python_value}, {self.inputs['Seed'].python_value})"
            else:
                self.outputs[0].python_value = f"random_float({self.inputs['Minimum'].python_value}, {self.inputs['Maximum'].python_value}, {self.inputs['Seed'].python_value})"
        else:
            if self.number_type == "Integer":
                self.outputs[0].python_value = f"random.randint(int({self.inputs['Minimum'].python_value}), int({self.inputs['Maximum'].python_value}))"
            else:
                self.outputs[0].python_value = f"random.uniform({self.inputs['Minimum'].python_value}, {self.inputs['Maximum'].python_value})"

    def draw_node(self, context, layout):
        layout.prop(self, "number_type")