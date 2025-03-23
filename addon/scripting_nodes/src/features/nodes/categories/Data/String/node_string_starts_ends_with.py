from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_String_Starts_Ends_With(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_String_Starts_Ends_With"
    bl_label = "String Starts/Ends With"
    bl_description = "Check if an input string starts or ends with another string"
    bl_width_default = 200

    def update_detection_mode(self, context):
        self._generate()

    def update_case_sensitive(self, context):
        self._generate()

    case_sensitive: bpy.props.BoolProperty(
        name="Case Sensitive", default=True, update=update_case_sensitive, description="Disable to match words regardless of capitalization. For example, a search starting with 'App' will also match 'application' and 'APPle'."
    )

    detection_mode: bpy.props.EnumProperty(
        items=[
            ("STARTSWITH", "Starts With", "Check if a string starts with another string"),
            ("ENDSWITH", "Ends With", "Check if a string ends with another string"),
        ],
        name="Method", default="STARTSWITH", update=update_detection_mode,
    )

    def on_create(self):
        self.add_input("ScriptingStringSocket", label="String")
        self.add_input("ScriptingStringSocket", label="Compare")
        self.add_output("ScriptingBooleanSocket", label="Result")

    def draw(self, context, layout):
        layout.prop(self, "case_sensitive", text="Case Sensitive")
        row = layout.row()
        row.prop(self, "detection_mode", text="")

    def generate(self):
        if self.detection_mode == "STARTSWITH":
            self.outputs[0].code = (
                f"(False if not {self.inputs[1].eval()} else "
                f"({self.inputs[0].eval()}.startswith({self.inputs[1].eval()}) " 
                f"if {self.case_sensitive} else {self.inputs[0].eval()}.lower().startswith({self.inputs[1].eval()}.lower())))"
            )
        else:
            self.outputs[0].code = (
                f"(False if not {self.inputs[1].eval()} else "
                f"({self.inputs[0].eval()}.endswith({self.inputs[1].eval()}) " 
                f"if {self.case_sensitive} else {self.inputs[0].eval()}.lower().endswith({self.inputs[1].eval()}.lower())))"
            )
