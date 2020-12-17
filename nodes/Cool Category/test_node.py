import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_TestNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_TestNode"
    bl_label = "Test"
    bl_icon = "GRAPH"
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
        "starts_tree": False,
        "import_once": False,
        "evaluate_once": False,
        "register_once": False,
        "unregister_once": False,
        "imperative_once": False,
    }
    
    def on_create(self,context):
        self.add_execute_input("Program")
        self.add_string_input("lol")
        self.add_execute_output("Program")

    def code_evaluate(self, context, main_tree, touched_socket):
        return {
            "code": f"""
                    # this worked i think {self.inputs[1].value}
                        # but this won't
                    """
        }