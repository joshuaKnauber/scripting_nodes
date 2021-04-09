import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_SetEditSelectNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetEditSelectNode"
    bl_label = "Set Edit Select Mode"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_execute_input("Set Edit Select Mode")
        self.add_execute_output("Execute").mirror_name = True
        inp = self.add_boolean_input("Vertex")
        inp.set_default(False)
        inp.disableable = True
        inp = self.add_boolean_input("Edge")
        inp.set_default(False)
        inp.disableable = True
        inp = self.add_boolean_input("Face")
        inp.set_default(False)
        inp.disableable = True


    def code_evaluate(self, context, touched_socket):

        vertex_execute = f"bpy.ops.mesh.select_mode(action='ENABLE' if {self.inputs[1].code()} else 'DISABLE', type='VERT', use_extend=True)" if self.inputs[1].enabled else ""
        edge_execute = f"bpy.ops.mesh.select_mode(action='ENABLE' if {self.inputs[2].code()} else 'DISABLE', type='EDGE', use_extend=True)" if self.inputs[2].enabled else ""
        face_execute = f"bpy.ops.mesh.select_mode(action='ENABLE' if {self.inputs[3].code()} else 'DISABLE', type='FACE', use_extend=True)" if self.inputs[3].enabled else ""

        return {
            "code": f"""
                    {vertex_execute}
                    {edge_execute}
                    {face_execute}
                    {self.outputs[0].code(5)}
                    """
        }
