import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_DebugDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DebugDataNode"
    bl_label = "Debug Data"
    bl_width_default = 200

    def on_create(self, context):
        self.add_data_input("Data")
        
    def draw_node(self, context, layout):
        if not self.inputs[0].is_linked:
            layout.label(text="This node might slow down your viewport!", icon="INFO")
        else:
            try:
                value = str(eval(self.inputs[0].python_value))
            except:
                value = "No Data"
            layout.label(text=value)