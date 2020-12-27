import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_CombineStringsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CombineStringsNode"
    bl_label = "Combine Strings"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_string_output("Combined String")
        self.add_string_input("String")
        self.add_dynamic_string_input("String")


    def code_evaluate(self, context, touched_socket):
        values = []
        for inp in self.inputs[:-1]:
            if inp == self.inputs[-2]:
                values.append(inp.value)
            else:
                values.append(inp.value + " + ")

        return {
            "code": f"""{self.list_blocks(values, 0)}"""
        }