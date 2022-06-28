import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import normalize_code



class SN_EnumMapInterfaceNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_EnumMapInterfaceNode"
    bl_label = "Enum Map (Interface)"
    bl_width_default = 200
    node_color = "INTERFACE"
    
    passthrough_layout_type = True
    
    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Enum Value")
        self.add_interface_output("Interface")
        self.add_interface_output("Other Option")
        out = self.add_dynamic_interface_output("Enum Option")
        out.is_variable = True
        
    def on_socket_name_change(self, socket):
        self._evaluate(bpy.context)

    def evaluate(self, context):
        options = ""
        for out in self.outputs:
            if out.is_variable and not out.dynamic:
                option_code = self.indent(out.python_value, 7)
                option = f"""
                        {"el" if options else ""}if {self.inputs["Enum Value"].python_value} == "{out.name}":
                            {option_code}
                        """
                if option_code.strip():
                    options += normalize_code(option) + "\n"

        other_opt_code = self.indent(self.outputs['Other Option'].python_value, 6)
        self.code = f"""
                    {self.indent(options, 5)}
                    {"else:" if options.strip() else "if True:"}
                        {other_opt_code if other_opt_code.strip() else "pass"}
                    {self.indent(self.outputs[0].python_value, 5)}
                    """