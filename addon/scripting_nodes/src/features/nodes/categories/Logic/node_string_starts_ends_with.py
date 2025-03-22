from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_String_Starts_Ends_With(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_String_Starts_Ends_With"
    bl_label = "String Starts/Ends With"
    bl_description = "Check if an input string starts or ends with another string"

    def update_detection_mode(self, context):
        self._generate()

    detection_mode: bpy.props.EnumProperty(
        items=[
            ("STARTSWITH", "Starts With", "Check if a string starts with another string"),
            ("ENDSWITH", "Ends With", "Check if a string ends with another string"),
        ],
        name="Method", default="STARTSWITH", update=update_detection_mode,
    )

    def on_create(self):
        self.add_input("ScriptingBooleanSocket", label="Ignore Case Sensitivity")
        self.add_input("ScriptingStringSocket", label="String")
        self.add_input("ScriptingStringSocket", label="Startswith")
        self.add_input("ScriptingStringSocket", label="Endswith")
        self.add_output("ScriptingBooleanSocket", label="Result")
        self.inputs[0].value = False

    def draw(self, context, layout):
        row = layout.row()
        row.prop(self, "detection_mode", text="")

    def generate(self):
        self.inputs[2].enabled = self.detection_mode == "STARTSWITH"
        self.inputs[3].enabled = not self.detection_mode == "STARTSWITH"
        if self.detection_mode == "STARTSWITH":
            self.outputs[0].code = (
                f"(False if not {self.inputs[2].eval()} else "
                f"({self.inputs[1].eval()}.lower().startswith({self.inputs[2].eval()}.lower()) "
                f"if {self.inputs[0].eval()} else {self.inputs[1].eval()}.startswith({self.inputs[2].eval()})))"
            )
        else:
            self.outputs[0].code = (
                f"(False if not {self.inputs[3].eval()} else "
                f"({self.inputs[1].eval()}.lower().endswith({self.inputs[3].eval()}.lower()) "
                f"if {self.inputs[0].eval()} else {self.inputs[1].eval()}.endswith({self.inputs[3].eval()})))"
            )
