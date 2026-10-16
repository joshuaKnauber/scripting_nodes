import bpy

from .....lib.code_format import f_string
from .....sockets.spec import Data, Integer, List, String
from ....base_node import ScriptingBaseNode


class SNA_Node_SplitString(ScriptingBaseNode, bpy.types.Node):
    """Split a text into a list at a separator (spaces and line breaks
    without one)."""

    bl_idname = "SNA_Node_SplitString"
    bl_label = "Split String"
    sn_inputs = [
        String("string", "String"),
        String("separator", "Separator"),
        Integer("max_splits", "Max Splits", default=-1),
    ]
    sn_outputs = [List("list", "List")]

    def emit(self, ctx):
        string, separator = ctx.input("string"), ctx.input("separator")
        args = [f"{separator} or None"]
        if ctx.is_linked("max_splits") or self.socket("max_splits").value != -1:
            args.append(ctx.input("max_splits"))
        ctx.output("list", f"{string}.split({', '.join(args)})")


class SNA_Node_JoinList(ScriptingBaseNode, bpy.types.Node):
    """Join the items of a list into one text, with a separator between them."""

    bl_idname = "SNA_Node_JoinList"
    bl_label = "Join List"
    sn_inputs = [List("list", "List"), String("separator", "Separator", default=", ")]
    sn_outputs = [String("string", "String")]

    def emit(self, ctx):
        items = ctx.input("list")
        ctx.output("string", f"{ctx.input('separator')}.join(str(i) for i in {items})")


class SNA_Node_ReplaceString(ScriptingBaseNode, bpy.types.Node):
    """Replace every occurrence of a text with another."""

    bl_idname = "SNA_Node_ReplaceString"
    bl_label = "Replace String"
    sn_inputs = [
        String("string", "String"),
        String("find", "Find"),
        String("replace", "Replace"),
    ]
    sn_outputs = [String("string", "String")]

    def emit(self, ctx):
        string, find = ctx.input("string"), ctx.input("find")
        ctx.output("string", f"{string}.replace({find}, {ctx.input('replace')})")


class SNA_Node_SliceString(ScriptingBaseNode, bpy.types.Node):
    """Part of a text: from Start, Length characters (to the end with 0).
    Negative positions count from the end."""

    bl_idname = "SNA_Node_SliceString"
    bl_label = "Slice String"
    sn_inputs = [
        String("string", "String"),
        Integer("start", "Start"),
        Integer("length", "Length", default=0),
    ]
    sn_outputs = [String("string", "String")]

    def emit(self, ctx):
        string, start = ctx.input("string"), ctx.input("start")
        length = self.socket("length")
        if not length.is_linked and length.value == 0:
            ctx.output("string", f"{string}[{start}:]")
            return
        end = f"{start} + {ctx.input('length')}"
        ctx.output("string", f"{string}[{start}:({end}) or None]")


class SNA_Node_StringLength(ScriptingBaseNode, bpy.types.Node):
    """The number of characters of a text."""

    bl_idname = "SNA_Node_StringLength"
    bl_label = "String Length"
    sn_inputs = [String("string", "String")]
    sn_outputs = [Integer("length", "Length")]

    def emit(self, ctx):
        ctx.output("length", f"len({ctx.input('string')})")


CASES = [
    ("upper", "UPPER CASE", "All letters upper case"),
    ("lower", "lower case", "All letters lower case"),
    ("title", "Title Case", "Every word starts with an upper case letter"),
    ("capitalize", "Capitalize", "Only the first letter upper case"),
    ("swapcase", "sWAP cASE", "Upper case letters lower case and the other way"),
]


class SNA_Node_ChangeCase(ScriptingBaseNode, bpy.types.Node):
    """Change a text to upper case, lower case, title case, ..."""

    bl_idname = "SNA_Node_ChangeCase"
    bl_label = "Change Case"
    sn_inputs = [String("string", "String")]
    sn_outputs = [String("string", "String")]
    sn_header_props = ("case",)

    case: bpy.props.EnumProperty(name="Case", items=CASES)

    def emit(self, ctx):
        ctx.output("string", f"{ctx.input('string')}.{self.case}()")


TRIM_SIDES = [
    ("strip", "Both", "Remove characters at the start and the end"),
    ("lstrip", "Start", "Remove characters at the start"),
    ("rstrip", "End", "Remove characters at the end"),
]


class SNA_Node_TrimString(ScriptingBaseNode, bpy.types.Node):
    """Remove spaces and line breaks (or the given characters) at the start
    and end of a text."""

    bl_idname = "SNA_Node_TrimString"
    bl_label = "Trim String"
    sn_inputs = [String("string", "String"), String("characters", "Characters")]
    sn_outputs = [String("string", "String")]

    side: bpy.props.EnumProperty(name="Side", items=TRIM_SIDES)

    def draw(self, context, layout):
        layout.prop(self, "side", expand=True)

    def emit(self, ctx):
        characters = self.socket("characters")
        args = ""
        if characters.is_linked or characters.value:
            args = f"{ctx.input('characters')} or None"
        ctx.output("string", f"{ctx.input('string')}.{self.side}({args})")


PAD_ALIGNMENTS = [
    ("ljust", "Left", "Fill at the end"),
    ("center", "Center", "Fill on both sides"),
    ("rjust", "Right", "Fill at the start (numbers: 007)"),
]


class SNA_Node_PadString(ScriptingBaseNode, bpy.types.Node):
    """Fill a text up to a length, e.g. numbers with leading zeros."""

    bl_idname = "SNA_Node_PadString"
    bl_label = "Pad String"
    sn_inputs = [
        String("string", "String"),
        Integer("length", "Length", default=3),
        String("fill", "Fill", default="0"),
    ]
    sn_outputs = [String("string", "String")]

    alignment: bpy.props.EnumProperty(
        name="Alignment", items=PAD_ALIGNMENTS, default="rjust"
    )

    def draw(self, context, layout):
        layout.prop(self, "alignment", expand=True)

    def emit(self, ctx):
        string, length = ctx.input("string"), ctx.input("length")
        # str.ljust() & co. take exactly one character
        fill = f"({ctx.input('fill')} or ' ')[0]"
        ctx.output("string", f"{string}.{self.alignment}({length}, {fill})")


class SNA_Node_FormatString(ScriptingBaseNode, bpy.types.Node):
    """Put values into a text: each {} is replaced by the next value.
    {:.2f} rounds a number to two decimals, {:03} pads it with zeros."""

    bl_idname = "SNA_Node_FormatString"
    bl_label = "Format String"
    sn_inputs = [
        String("format", "Format", default="{} items"),
        Data("value", "Value", dynamic=True),
    ]
    sn_outputs = [String("string", "String")]

    def emit(self, ctx):
        values = ctx.inputs("value")
        template = self.socket("format")
        if not template.is_linked:
            code = f_string(template.value, values)
            if code is not None:
                ctx.output("string", code)
                return
        ctx.output("string", f"{ctx.input('format')}.format({', '.join(values)})")


class SNA_Node_FindInString(ScriptingBaseNode, bpy.types.Node):
    """Where a text first appears in another (-1 if it doesn't), and how
    often it appears."""

    bl_idname = "SNA_Node_FindInString"
    bl_label = "Find in String"
    sn_inputs = [String("string", "String"), String("find", "Find")]
    sn_outputs = [Integer("index", "Index"), Integer("count", "Count")]

    def emit(self, ctx):
        string, find = ctx.input("string"), ctx.input("find")
        ctx.output("index", f"{string}.find({find})")
        ctx.output("count", f"{string}.count({find})")
