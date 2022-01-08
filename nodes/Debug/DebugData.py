import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_DebugDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DebugDataNode"
    bl_label = "Debug Data"
    bl_width_default = 200

    def on_create(self, context):
        self.add_data_input("Data")
        self.add_data_output("Data")
        
    def on_link_insert(self, from_socket, to_socket, is_output):
        if not is_output:
            self.convert_socket(self.outputs[0], from_socket.bl_idname)
            self._evaluate(bpy.context)
            
    def on_link_remove(self, from_socket, to_socket, is_output):
        if not is_output:
            self.convert_socket(self.outputs[0], self.socket_names["Data"])
            self._evaluate(bpy.context)
            
    def evaluate(self, context):
        self.outputs[0].python_value = self.inputs[0].python_value
        
    def draw_node(self, context, layout):
        try:
            value = str(eval(self.inputs[0].python_value))
        except:
            value = "No Data"
        layout.label(text=value)