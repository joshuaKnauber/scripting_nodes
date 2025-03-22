from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Remove_Whitespaces_In_String(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Remove_Whitespaces_In_String"
    bl_label = "Remove Whitespaces In String"
    bl_width_default = 200
    bl_description = "Remove whitespaces from a string also known as stripping"

    def update_stripping(self, context):
        self._generate()

    position: bpy.props.EnumProperty(
        items=[
            ("BOTH", "Both", "Remove whitespaces from both sides"),
            ("LEFT", "Left", "Remove whitespaces from left side"),
            ("RIGHT", "Right", "Remove whitespaces from right side"),
        ],
        name="Strip Method", default="BOTH", update=update_stripping,
    )

    def on_create(self):
        self.add_input("ScriptingStringSocket", label="String")
        self.add_output("ScriptingStringSocket",label="String")

    def draw(self, context, layout):
        row = layout.row()
        row.prop(self, "position", text="")

    def generate(self):
        if self.position == "BOTH":
            self.outputs[0].code = f"{self.inputs[0].eval()}.strip()"
        elif self.position == "LEFT":
            self.outputs[0].code = f"{self.inputs[0].eval()}.lstrip()"
        elif self.position == "RIGHT":
            self.outputs[0].code = f"{self.inputs[0].eval()}.rstrip()"
