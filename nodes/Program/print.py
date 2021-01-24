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
        self.add_execute_input("Print")
        self.add_execute_output("Execute").mirror_name = True
        self.add_string_input("Content").removable = True
        self.add_dynamic_string_input("Content")


    def code_evaluate(self, context, touched_socket):
        
        if self.addon_tree.doing_export:
            return {
                "code": f"""
                        print({self.inputs["Content"].by_name(separator=", ")})
                        {self.outputs[0].code(6)}
                        """
            }
            
        else:
            return {
                "code": f"""
                        sn_print("{self.addon_tree.name}",{self.inputs["Content"].by_name(separator=", ")})
                        {self.outputs[0].code(6)}
                        """
            }