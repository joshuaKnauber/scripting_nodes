"""File Handler: files dragged onto Blender run an operator of this add-on
(bpy.types.FileHandler). The operator picks files with a File Browser; a
dropped file is set before it starts, so it runs without the browser."""

import bpy

from ....core import naming
from ....core.context import NodeError
from ....core.references import Reference
from ....sockets.spec import String
from ...base_node import ScriptingBaseNode
from ..data.blender_data.node_context_checks import rna_items


def _file_operator(owner, target):
    return target.invoke_type == "FILE_BROWSER" and target.file_mode in {
        "OPEN_FILE",
        "OPEN_FILES",
    }


class SNA_Node_FileHandler(ScriptingBaseNode, bpy.types.Node):
    """Run an operator when files are dragged onto Blender, e.g. .csv files
    into the 3D Viewport. The operator's Invoke Type is File Browser."""

    bl_idname = "SNA_Node_FileHandler"
    bl_label = "File Handler"
    bl_width_default = 200
    sn_root = True
    sn_inputs = [
        String("label", "Label", default="Import"),
        String("extensions", "Extensions", default=".txt;.csv"),
    ]

    operator: Reference(
        ("SNA_Node_Operator",),
        name="Operator",
        description="An Operator node opening files (Invoke Type File Browser)",
        filter=_file_operator,
    )
    area_type: bpy.props.EnumProperty(
        name="Drop In",
        items=[("ANY", "Any Editor", "", "WINDOW", 1000)]
        + rna_items("Area", "type", skip=("EMPTY",)),
        default="VIEW_3D",
    )

    def sn_names(self):
        return [naming.Class("class", "FH", naming.label(self))]

    def draw(self, context, layout):
        self.draw_reference(layout, "operator")
        layout.prop(self, "area_type", text="")

    def emit(self, ctx):
        target = ctx.resolve("operator")
        if target is None:
            raise NodeError("Pick an operator with Invoke Type File Browser")
        if not _file_operator(self, target):
            raise NodeError("The operator needs Invoke Type File Browser (open files)")
        extensions = self.socket("extensions")
        if not extensions.is_linked and not extensions.value.strip():
            raise NodeError("List the file extensions, e.g. .txt;.csv")
        poll = ""
        if self.area_type != "ANY":
            poll = f"""
                @classmethod
                def poll_drop(cls, context):
                    return context.area is not None and context.area.type == {self.area_type!r}
            """
        name = ctx.name("class")
        ctx.module(f"""
            class {name}(bpy.types.FileHandler):
                bl_idname = {name!r}
                bl_label = {ctx.input("label")}
                bl_import_operator = {target.operator_idname!r}
                bl_file_extensions = {ctx.input("extensions")}
                {ctx.join([poll])}
        """)
