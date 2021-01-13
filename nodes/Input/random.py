import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_RandomNumberNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RandomNumberNode"
    bl_label = "Random Number"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3)
    }


    def on_create(self,context):
        self.add_integer_output("Random Integer")
        self.add_float_output("Random Float")
        self.add_float_input("Min")
        self.add_float_input("Max")


    def code_evaluate(self, context, touched_socket):
        from_to = self.inputs[0].code() + ", " + self.inputs[1].code()

        if touched_socket == self.outputs[0]:
            return {
                "code": f"""random.randint(int(min({from_to})), int(max({from_to})))"""
            }
        return {
            "code": f"""random.uniform(min({from_to}), max({from_to}))"""
        }


    def code_imports(self, context):
        return {
            "code": f"""import random"""
        }