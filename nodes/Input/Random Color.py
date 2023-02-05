import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_RandomColorNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_RandomColorNode"
    bl_label = "Random Color"
    node_color = "VECTOR"

    def on_create(self, context):
        self.add_boolean_input("Use Alpha")
        inp = self.add_float_input("Fixed Alpha")
        inp.can_be_disabled = True
        inp.disabled = True
        inp.default_value = 1.0
        inp = self.add_integer_input("Seed")
        inp.can_be_disabled = True
        inp.disabled = True
        self.add_float_vector_output("Random Color").subtype = "COLOR"

    def evaluate(self, context):
        self.code_import = "import random"
        self.code_imperative = """
        def random_color(use_alpha, fixed_alpha, seed):
            random.seed(seed)
            if use_alpha:
                return (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), fixed_alpha if fixed_alpha != None else random.uniform(0, 1))
            else:
                return (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
        """
        self.outputs[0].python_value = f"random_color({self.inputs['Use Alpha'].python_value}, {'None' if self.inputs['Fixed Alpha'].disabled else self.inputs['Fixed Alpha'].python_value}, {'None' if self.inputs['Seed'].disabled else self.inputs['Seed'].python_value})"