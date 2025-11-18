import bpy
from ...base_node import SN_ScriptingBaseNode
from ....utils import normalize_code



class SN_EnumMapNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_EnumMapNode"
    bl_label = "Enum Map (Execute)"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_string_input("Enum Value")
        self.add_execute_output("Continue")
        self.add_execute_output("Other Option")
        out = self.add_dynamic_execute_output("Enum Option")
        out.is_variable = True
        
    def on_socket_name_change(self, socket):
        # Prevent recursion
        storage_key = f"_socket_updating_name_{id(socket)}"
        if self.get(storage_key, False):
            return
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
                    {self.indent(self.outputs['Continue'].python_value, 5)}
                    """