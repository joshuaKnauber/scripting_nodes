import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_GetDataScriptlineNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetDataScriptlineNode"
    bl_label = "Get Data Scriptline"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("Line")
        self.add_data_output("Data").changeable = True
        
    def evaluate(self, context):
        if self.outputs[0].bl_label == "Property" or self.outputs[0].bl_label == "Collection Property":
            self.outputs[0].python_value = f"{self.inputs[0].python_value}"
        else:
            self.outputs[0].python_value = f"eval({self.inputs[0].python_value})"
        
    def draw_node(self, context, layout):
        if self.outputs[0].bl_label == "Property" or self.outputs[0].bl_label == "Collection Property":
            box = layout.box()
            col = box.column(align=True)
            col.label(text="(prop_source, 'prop_name', prop_index)")
            col.label(text="e.g. (bpy.data, 'objects', 'Cube')")
            col.label(text="e.g. (bpy.context, 'active_object')")