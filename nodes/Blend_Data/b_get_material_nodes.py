import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_GetMaterialNodesNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetMaterialNodesNode"
    bl_label = "Get Material Nodes"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
        "imperative_once": True
    }
    
    
    def on_create(self,context):
        inp = self.add_blend_data_input("Material")
        inp.data_type = "Material"
        inp.data_identifier = "material"
        inp.data_name = "Material"
        out = self.add_blend_data_output("Nodes")
        out.subtype = "COLLECTION"
        out.data_type = "Node"
        out.data_name = "Node"
        out.data_identifier = "nodes"
        self.add_boolean_output("Use Nodes")
    
    

    def code_evaluate(self, context, touched_socket):
        if self.inputs[0].links:
            if touched_socket.socket_type == "BOOLEAN":
                return {
                    "code": f"{self.inputs[0].code()}.use_nodes"
                }
            else:
                return {
                    "code": f"{self.inputs[0].code()}.node_tree.nodes"
                }
        else:
            self.add_error("No blend data", "Blend data input is not connected", True)
            if touched_socket.socket_type == "BOOLEAN":
                return {
                        "code": "False"
                }
            else:
                return {
                        "code": "None"
                }