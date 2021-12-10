import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_DataLogNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DataLogNode"
    bl_label = "Data Log"

    def on_create(self, context):
        self.add_data_input("Data")
        self.add_data_output("Data")

    last_value: bpy.props.StringProperty()

    # TODO not done

    def evaluate(self, context):
        self.outputs["Data"].python_value = self.inputs["Data"].python_value
        try:
            self.last_value = str(eval(self.inputs["Data"].python_value))
        except:
            pass

    def draw_node(self, context, layout):
        layout.label(text=self.last_value)