import bpy

from .....sockets.spec import Boolean, Float, Integer, Interface
from ....base_node import ScriptingBaseNode


class SNA_Node_Split(ScriptingBaseNode, bpy.types.Node):
    """Two columns side by side: Factor is the share of the first."""

    bl_idname = "SNA_Node_Split"
    bl_label = "Split"
    sn_inputs = [
        Interface(),
        Float("factor", "Factor", default=0.5),
        Boolean("align", "Align"),
    ]
    sn_outputs = [
        Interface("first", "First"),
        Interface("second", "Second"),
        Interface("next", "After"),
    ]

    def emit(self, ctx):
        split, first, second = ctx.var("split"), ctx.var("column"), ctx.var("column")
        args = ctx.args(
            ctx.keyword("factor", "factor", 0.0), ctx.keyword("align", "align", False)
        )
        ctx.code(f"""
            {split} = {ctx.layout}.split({args})
            {first} = {split}.column()
            {ctx.flow("first", layout=first)}
            {second} = {split}.column()
            {ctx.flow("second", layout=second)}
            {ctx.flow("next")}
        """)


class SNA_Node_Grid(ScriptingBaseNode, bpy.types.Node):
    """Lay out the following elements in a grid. 0 columns: as many as fit."""

    bl_idname = "SNA_Node_Grid"
    bl_label = "Grid"
    sn_inputs = [
        Interface(),
        Integer("columns", "Columns", default=0),
        Boolean("even_columns", "Even Columns", default=True),
        Boolean("even_rows", "Even Rows", default=True),
        Boolean("align", "Align"),
    ]
    sn_outputs = [Interface("content", "Grid"), Interface("next", "After")]

    def emit(self, ctx):
        grid = ctx.var("grid")
        args = ctx.args(
            "row_major=True",
            ctx.keyword("columns", "columns", 0),
            ctx.keyword("even_columns", "even_columns", False),
            ctx.keyword("even_rows", "even_rows", False),
            ctx.keyword("align", "align", False),
        )
        ctx.code(f"""
            {grid} = {ctx.layout}.grid_flow({args})
            {ctx.flow("content", layout=grid)}
            {ctx.flow("next")}
        """)
