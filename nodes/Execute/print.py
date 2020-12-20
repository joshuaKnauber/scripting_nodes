import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_PrintNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PrintNode"
    bl_label = "Print"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_execute_input("Execute")
        self.add_execute_output("Execute")
        self.add_string_input("Content", True)
        self.add_dynamic_data_input("Content")


    def code_evaluate(self, context, main_tree, touched_socket):
        contents = []
        for inp in self.inputs[1:-1]:
            contents.append(inp.value + ", ")

        return {
            "code": f"""print({self.list_blocks(contents, 0)})"""
        }