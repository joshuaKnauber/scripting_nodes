from .....lib.utils.code.format import indent
from ....node_tree.code_gen.build_context import is_building
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
        # During the live editor pass, route prints to SN's canvas overlay so
        # debug output is visible without alt-tabbing to the console. The
        # exported build strips this - shipped addons just print().
        if is_building():
            self.code_inline = f"""
                print({text_eval})
                {next_code}
            """
        else:
            self.code_inline = f"""
                _sn_print_msg = str({text_eval})
                print(_sn_print_msg)
                _sn_overlay = bpy.app.driver_namespace.get("_sn_overlay_log")
                if _sn_overlay:
                    _sn_overlay("INFO", _sn_print_msg)
                {next_code}
            """
