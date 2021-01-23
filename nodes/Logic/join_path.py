import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_JoinPathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_JoinPathNode"
    bl_label = "Join Paths"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_string_input("Basepath").subtype = "DIRECTORY"
        self.add_dynamic_string_input("Path Part")
        self.add_string_output("Combined Path")


    def code_evaluate(self, context, touched_socket):
        
        return {
            "code": f"os.path.join({self.inputs[0].code()},{self.inputs[1].by_name(separator=',')})"
        }