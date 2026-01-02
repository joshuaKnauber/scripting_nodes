from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_Print(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Print"
    bl_label = "Print"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingStringSocket", "Text")
        self.add_output("ScriptingProgramSocket")

    def generate(self):
        text_eval = self.inputs[1].eval()
        next_code = indent(self.outputs[0].eval(), 3)

        if bpy.context.scene.sna.addon.build_with_production_code:
            self.code = f"""
            print({text_eval})
            {next_code} 
        """
        else:
            self.code = f"""
            _print_msg = {text_eval}
            print(_print_msg)
            try:
                from .....handlers.draw.log_overlay import add_log
                add_log("INFO", str(_print_msg))
            except: pass
            {next_code} 
        """
