import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ReportNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_ReportNode"
    bl_label = "Report"
    node_color = "PROGRAM"

    def on_create(self, context):
        self.add_execute_input()
        self.add_string_input()
        self.add_execute_output()

    type: bpy.props.EnumProperty(name="Type",
                                description="Type of the report message",
                                items=[("INFO", "Info", "Info"),
                                       ("WARNING", "Warning", "Warning"),
                                       ("ERROR", "Error", "Error")],
                                update=SN_ScriptingBaseNode._evaluate)

    def evaluate(self, context):
        self.code = f"""
                    self.report({{'{self.type}'}}, message={self.inputs[1].python_value})
                    {self.indent(self.outputs[0].python_value, 5)}
                    """
                    
    def draw_node(self, context, layout):
        layout.prop(self, "type")
        layout.label(text="This only works when connected to operators", icon="INFO")