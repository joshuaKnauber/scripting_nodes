import bpy

from .....sockets.spec import Boolean, Data, Flow, Integer, List
from ....base_node import ScriptingBaseNode

# -----------------------------------------------------------------------------
# Values
# -----------------------------------------------------------------------------


class SNA_Node_CreateList(ScriptingBaseNode, bpy.types.Node):
    """Create a list from multiple inputs"""

    bl_idname = "SNA_Node_CreateList"
    bl_label = "Create List"
    sn_inputs = [Data("item", "Item", dynamic=True)]
    sn_outputs = [List("list", "List")]

    def emit(self, ctx):
        ctx.output("list", f"[{', '.join(ctx.inputs('item'))}]")


class SNA_Node_ListGetItem(ScriptingBaseNode, bpy.types.Node):
    """Get an item from a list at a specific index"""

    bl_idname = "SNA_Node_ListGetItem"
    bl_label = "List Get Item"
    sn_inputs = [List("list", "List"), Integer("index", "Index")]
    sn_outputs = [Data("item", "Item")]

    def emit(self, ctx):
        items, index = ctx.input("list"), ctx.input("index")
        ctx.output("item", f"{items}[{index}] if len({items}) > {index} else None")


class SNA_Node_ListLength(ScriptingBaseNode, bpy.types.Node):
    """Get the length of a list"""

    bl_idname = "SNA_Node_ListLength"
    bl_label = "List Length"
    sn_inputs = [List("list", "List")]
    sn_outputs = [Integer("length", "Length")]

    def emit(self, ctx):
        ctx.output("length", f"len({ctx.input('list')})")


class SNA_Node_ListIndex(ScriptingBaseNode, bpy.types.Node):
    """Find the index of an item in a list"""

    bl_idname = "SNA_Node_ListIndex"
    bl_label = "List Index"
    sn_inputs = [List("list", "List"), Data("item", "Item")]
    sn_outputs = [Integer("index", "Index"), Boolean("found", "Found")]

    def emit(self, ctx):
        items, item = ctx.input("list"), ctx.input("item")
        ctx.output("index", f"{items}.index({item}) if {item} in {items} else -1")
        ctx.output("found", f"{item} in {items}")


class SNA_Node_ListContains(ScriptingBaseNode, bpy.types.Node):
    """Check if a list contains an item"""

    bl_idname = "SNA_Node_ListContains"
    bl_label = "List Contains"
    sn_inputs = [List("list", "List"), Data("item", "Item")]
    sn_outputs = [Boolean("contains", "Contains")]

    def emit(self, ctx):
        ctx.output("contains", f"{ctx.input('item')} in {ctx.input('list')}")


class SNA_Node_ListSlice(ScriptingBaseNode, bpy.types.Node):
    """Get a slice of a list"""

    bl_idname = "SNA_Node_ListSlice"
    bl_label = "List Slice"
    sn_inputs = [
        List("list", "List"),
        Integer("start", "Start", default=0),
        Integer("end", "End", default=0),
    ]
    sn_outputs = [List("slice", "Slice")]

    def emit(self, ctx):
        end = ctx.input("end")
        # an unconnected End of 0 means "until the end of the list"
        if not ctx.is_linked("end") and self.socket("end").value == 0:
            end = "None"
        ctx.output("slice", f"{ctx.input('list')}[{ctx.input('start')}:{end}]")


# -----------------------------------------------------------------------------
# Statements
# -----------------------------------------------------------------------------


class SNA_Node_ListAppend(ScriptingBaseNode, bpy.types.Node):
    """Append an item to the end of a list"""

    bl_idname = "SNA_Node_ListAppend"
    bl_label = "List Append"
    sn_inputs = [Flow(), List("list", "List"), Data("item", "Item")]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        ctx.code(f"""
            {ctx.input("list")}.append({ctx.input("item")})
            {ctx.flow("next")}
        """)


class SNA_Node_ListInsert(ScriptingBaseNode, bpy.types.Node):
    """Insert an item at a specific index"""

    bl_idname = "SNA_Node_ListInsert"
    bl_label = "List Insert"
    sn_inputs = [
        Flow(),
        List("list", "List"),
        Integer("index", "Index"),
        Data("item", "Item"),
    ]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        ctx.code(f"""
            {ctx.input("list")}.insert({ctx.input("index")}, {ctx.input("item")})
            {ctx.flow("next")}
        """)


class SNA_Node_ListRemove(ScriptingBaseNode, bpy.types.Node):
    """Remove the first occurrence of an item from a list"""

    bl_idname = "SNA_Node_ListRemove"
    bl_label = "List Remove"
    sn_inputs = [Flow(), List("list", "List"), Data("item", "Item")]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        items, item = ctx.input("list"), ctx.input("item")
        ctx.code(f"""
            if {item} in {items}:
                {items}.remove({item})
            {ctx.flow("next")}
        """)


class SNA_Node_ListPop(ScriptingBaseNode, bpy.types.Node):
    """Remove and return an item at a specific index"""

    bl_idname = "SNA_Node_ListPop"
    bl_label = "List Pop"
    sn_inputs = [Flow(), List("list", "List"), Integer("index", "Index", default=-1)]
    sn_outputs = [Flow("next"), Data("item", "Item")]

    def emit(self, ctx):
        items = ctx.input("list")
        popped = ctx.var("popped")
        ctx.output("item", popped)
        ctx.code(f"""
            {popped} = {items}.pop({ctx.input("index")}) if {items} else None
            {ctx.flow("next")}
        """)


class SNA_Node_ListSetItem(ScriptingBaseNode, bpy.types.Node):
    """Set an item in a list at a specific index"""

    bl_idname = "SNA_Node_ListSetItem"
    bl_label = "List Set Item"
    sn_inputs = [
        Flow(),
        List("list", "List"),
        Integer("index", "Index"),
        Data("item", "Item"),
    ]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        items, index = ctx.input("list"), ctx.input("index")
        ctx.code(f"""
            if len({items}) > {index}:
                {items}[{index}] = {ctx.input("item")}
            {ctx.flow("next")}
        """)


class SNA_Node_ListClear(ScriptingBaseNode, bpy.types.Node):
    """Clear all items from a list"""

    bl_idname = "SNA_Node_ListClear"
    bl_label = "List Clear"
    sn_inputs = [Flow(), List("list", "List")]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        ctx.code(f"""
            {ctx.input("list")}.clear()
            {ctx.flow("next")}
        """)


class SNA_Node_ListExtend(ScriptingBaseNode, bpy.types.Node):
    """Extend a list by appending all items from another list"""

    bl_idname = "SNA_Node_ListExtend"
    bl_label = "List Extend"
    sn_inputs = [Flow(), List("list", "List"), List("items", "Items")]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        ctx.code(f"""
            {ctx.input("list")}.extend({ctx.input("items")})
            {ctx.flow("next")}
        """)


class SNA_Node_ListReverse(ScriptingBaseNode, bpy.types.Node):
    """Reverse a list in place"""

    bl_idname = "SNA_Node_ListReverse"
    bl_label = "List Reverse"
    sn_inputs = [Flow(), List("list", "List")]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        ctx.code(f"""
            {ctx.input("list")}.reverse()
            {ctx.flow("next")}
        """)


class SNA_Node_ListSort(ScriptingBaseNode, bpy.types.Node):
    """Sort a list in place"""

    bl_idname = "SNA_Node_ListSort"
    bl_label = "List Sort"
    sn_inputs = [Flow(), List("list", "List")]
    sn_outputs = [Flow("next")]

    reverse: bpy.props.BoolProperty(
        name="Reverse",
        description="Sort in descending order",
        default=False,
    )

    def draw(self, context, layout):
        layout.prop(self, "reverse")

    def emit(self, ctx):
        ctx.code(f"""
            {ctx.input("list")}.sort(reverse={self.reverse!r})
            {ctx.flow("next")}
        """)


class SNA_Node_ForEachList(ScriptingBaseNode, bpy.types.Node):
    """Iterate over each item in a list"""

    bl_idname = "SNA_Node_ForEachList"
    bl_label = "For Each (List)"
    sn_inputs = [Flow(), List("list", "List")]
    sn_outputs = [
        Flow("loop", "Loop"),
        Flow("next", "Done"),
        Data("item", "Item"),
        Integer("index", "Index"),
    ]

    def emit(self, ctx):
        item, index = ctx.var("item"), ctx.var("index")
        loop = ctx.flow("loop", outputs={"item": item, "index": index})
        ctx.code(f"""
            for {index}, {item} in enumerate({ctx.input("list")}):
                {loop}
            {ctx.flow("next")}
        """)
