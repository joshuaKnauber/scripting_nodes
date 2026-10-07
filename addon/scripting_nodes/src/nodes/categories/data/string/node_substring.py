import bpy

from .....sockets.spec import Boolean, String
from ....base_node import ScriptingBaseNode


class SNA_Node_Substring(ScriptingBaseNode, bpy.types.Node):
    """Whether a text contains another text."""

    bl_idname = "SNA_Node_Substring"
    bl_label = "Substring In String"
    sn_inputs = [String("string", "String"), String("substring", "Substring")]
    sn_outputs = [Boolean("is_in", "Is in String")]

    case_sensitive: bpy.props.BoolProperty(name="Case Sensitive", default=True)

    def draw(self, context, layout):
        layout.prop(self, "case_sensitive", text="Case Sensitive")

    def emit(self, ctx):
        string = ctx.input("string")
        substring = ctx.input("substring")
        if self.case_sensitive:
            ctx.output("is_in", f"{substring} in {string}")
        else:
            ctx.output("is_in", f"{substring}.lower() in {string}.lower()")
