import bpy

from .....sockets.spec import Boolean, String
from ....base_node import ScriptingBaseNode

MODES = [
    ("CONTAINS", "Contains", "The text appears anywhere in the string"),
    ("STARTS", "Starts With", "The string starts with the text"),
    ("ENDS", "Ends With", "The string ends with the text"),
]


class SNA_Node_Substring(ScriptingBaseNode, bpy.types.Node):
    """Whether a text contains another text, starts or ends with it."""

    bl_idname = "SNA_Node_Substring"
    bl_label = "Substring In String"
    sn_inputs = [String("string", "String"), String("substring", "Substring")]
    sn_outputs = [Boolean("is_in", "Is in String")]
    sn_header_props = ("mode",)

    mode: bpy.props.EnumProperty(name="Mode", items=MODES)
    case_sensitive: bpy.props.BoolProperty(name="Case Sensitive", default=True)

    def draw(self, context, layout):
        layout.prop(self, "case_sensitive", text="Case Sensitive")

    def emit(self, ctx):
        string = ctx.input("string")
        substring = ctx.input("substring")
        if not self.case_sensitive:
            string, substring = f"{string}.lower()", f"{substring}.lower()"
        if self.mode == "STARTS":
            ctx.output("is_in", f"{string}.startswith({substring})")
        elif self.mode == "ENDS":
            ctx.output("is_in", f"{string}.endswith({substring})")
        else:
            ctx.output("is_in", f"{substring} in {string}")
