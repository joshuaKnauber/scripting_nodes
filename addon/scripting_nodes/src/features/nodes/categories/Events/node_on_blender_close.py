from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_OnBlenderClose(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_OnBlenderClose"
    bl_label = "On Blender Close"
    sn_options = {"ROOT_NODE"}

    def on_create(self):
        self.add_output("ScriptingLogicSocket")

    @property
    def handler_name(self):
        return f"before_exit_handler_{self.id}"

    def generate(self):
        output_code = self.outputs[0].eval()

        self.code_imports = "import atexit"

        self.code_module = f"""
def {self.handler_name}():
    {indent(output_code, 1) if output_code.strip() else 'pass'}
"""

        self.code_register = f"atexit.register({self.handler_name})"
        self.code_unregister = f"atexit.unregister({self.handler_name})"
