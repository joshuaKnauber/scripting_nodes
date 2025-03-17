from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_CombineString(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_CombineString"
    bl_label = "Combine String"
    bl_width_default = 180

    def on_create(self):
        inp = self.add_input("ScriptingStringSocket", "String")
        inp.is_dynamic = True
        inp = self.add_input("ScriptingDynamicAddInputSocket", "Add Input")
        inp.add_socket_type = "ScriptingStringSocket"
        inp.add_socket_name = "String"

        self.add_output("ScriptingStringSocket", "Combined String")

    def generate(self):
        string_inputs = [
            inp.eval()
            for inp in self.inputs
            if inp.bl_idname == "ScriptingStringSocket"
        ]

        if not string_inputs:
            self.outputs[0].code = '""'
        else:
            self.outputs[0].code = f"({' + '.join(string_inputs)})"
