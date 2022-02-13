import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_SetEditSelectNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetEditSelectNode"
    bl_label = "Set Edit Select"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.add_boolean_input("Vertex").can_be_disabled = True
        self.add_boolean_input("Edge").can_be_disabled = True
        self.add_boolean_input("Face").can_be_disabled = True

    def evaluate(self, context):
        vertex_execute = f"bpy.ops.mesh.select_mode(action='ENABLE' if {self.inputs[1].python_value} else 'DISABLE', type='VERT', use_extend=True)" if not self.inputs[1].disabled else ""
        edge_execute = f"bpy.ops.mesh.select_mode(action='ENABLE' if {self.inputs[2].python_value} else 'DISABLE', type='EDGE', use_extend=True)" if not self.inputs[2].disabled else ""
        face_execute = f"bpy.ops.mesh.select_mode(action='ENABLE' if {self.inputs[3].python_value} else 'DISABLE', type='FACE', use_extend=True)" if not self.inputs[3].disabled else ""

        self.code = f"""
                    {vertex_execute}
                    {edge_execute}
                    {face_execute}
                    {self.indent(self.outputs[0].python_value, 5)}
                    """