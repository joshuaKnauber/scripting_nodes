import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_TestNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_TestNode"
    bl_label = "Test"
    bl_icon = "GRAPH"
    
    node_options = {
        "starts_tree": False,
        "default_color": (0.3,0.3,0.3)
    }
    
    def on_create(self,context):
        self.add_execute_input("Program")
        self.add_execute_output("Program")
        self.add_dynamic_data_input("lol")
        
    def code_evaluate(self, context, main_tree, socket_data, touched_socket):
        pass