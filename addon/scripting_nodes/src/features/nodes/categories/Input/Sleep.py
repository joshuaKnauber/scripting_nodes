from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy
import time

class SN_SleepNode(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SleepNode"
    bl_label = "Sleep"

    def update_data_type(self, context):
        self._generate()


    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingFloatSocket", "Seconds")
        self.add_output("ScriptingProgramSocket")


    def generate(self):
        self.code_import = "import time"
        self.code = f"""
            var_{self.id} =  time.sleep({self.inputs[1].eval()})
            {indent(self.outputs[0].eval(), 3)}
        """
        self.outputs[0].code = f"var_{self.id}"
