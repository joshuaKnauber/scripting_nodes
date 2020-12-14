import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_TestNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_TestNode"
    bl_label = "Test"
    bl_icon = "GRAPH"
    node_color = (0.3,0.3,0.3)
    
    
    def on_create(self,context):
        self.add_execute_input("execute")
        self.add_execute_output("execute")
        self.add_dynamic_data_input("dynamic in")
        self.add_dynamic_data_output("dynamic out")
        self.add_string_output("string out")
        self.add_string_input("string inp")