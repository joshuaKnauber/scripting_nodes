import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_OtherTestNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_OtherTestNode"
    bl_label = "Other Test"
    bl_icon = "GRAPH"
    
    node_options = {
        "starts_tree": True,
        "default_color": (0.3,0.3,0.3)
    }

    def on_create(self,context):
        self.add_execute_output("Program")
        self.add_string_output("help")
        
    def code_evaluate(self, context, main_tree, touched_socket):
        return {
            "code": """
                    def test():
                        pass
                        {{my_socket}}
                    """,
            "data": {
                "my_socket": self.outputs[0]
            }
        }