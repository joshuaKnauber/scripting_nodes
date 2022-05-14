import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_StripStringNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_StripStringNode"
    bl_label = "Strip String"
    node_color = "STRING"
    bl_width_default = 200
    
    position: bpy.props.EnumProperty(name="Position",
                                description="Sides of the string to strip",
                                items=[("BOTH", "Both", "Remove whitespace on both sides of the string"),
                                       ("LEFT", "Left", "Remove whitespace on the left side of the string"),
                                       ("RIGHT", "Right", "Remove whitespace on the right side of the string")],
                                update=SN_ScriptingBaseNode._evaluate)

    def on_create(self, context):
        self.add_string_input("String")
        self.add_string_output("Stripped String")

    def evaluate(self, context):
        if self.position == "BOTH":
            self.outputs["Stripped String"].python_value = f"{self.inputs['String'].python_value}.strip()"
        elif self.position == "LEFT":
            self.outputs["Stripped String"].python_value = f"{self.inputs['String'].python_value}.lstrip()"
        elif self.position == "RIGHT":
            self.outputs["Stripped String"].python_value = f"{self.inputs['String'].python_value}.rstrip()"
            
    def draw_node(self, context, layout):
        layout.prop(self, "position", expand=True)