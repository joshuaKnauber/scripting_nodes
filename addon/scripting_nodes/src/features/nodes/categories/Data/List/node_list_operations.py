from ....base_node import ScriptingBaseNode
from ......lib.utils.code.format import indent
import bpy


class SNA_Node_CreateList(ScriptingBaseNode, bpy.types.Node):
    """Create a list from multiple inputs"""

    bl_idname = "SNA_Node_CreateList"
    bl_label = "Create List"

    def on_create(self):
        # Add a dynamic input for list items
        socket = self.add_input("ScriptingDataSocket", "Item")
        socket.is_dynamic = True
        self.add_output("ScriptingListSocket", "List")

    def draw(self, context, layout):
        pass

    def generate(self):
        # Collect all connected items
        items = []
        for inp in self.inputs:
            if inp.is_linked:
                items.append(inp.eval())
            elif not inp.is_dynamic:
                items.append(inp.eval())

        items_code = ", ".join(items) if items else ""
        self.outputs["List"].code = f"[{items_code}]"


class SNA_Node_ListAppend(ScriptingBaseNode, bpy.types.Node):
    """Append an item to the end of a list"""

    bl_idname = "SNA_Node_ListAppend"
    bl_label = "List Append"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingDataSocket", "Item")
        self.add_output("ScriptingProgramSocket")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        item_code = self.inputs["Item"].eval("None")
        self.code = f"""
            {list_code}.append({item_code})
            {indent(self.outputs[0].eval(), 3)}
        """


class SNA_Node_ListInsert(ScriptingBaseNode, bpy.types.Node):
    """Insert an item at a specific index"""

    bl_idname = "SNA_Node_ListInsert"
    bl_label = "List Insert"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingIntegerSocket", "Index")
        self.add_input("ScriptingDataSocket", "Item")
        self.add_output("ScriptingProgramSocket")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        index_code = self.inputs["Index"].eval("0")
        item_code = self.inputs["Item"].eval("None")
        self.code = f"""
            {list_code}.insert({index_code}, {item_code})
            {indent(self.outputs[0].eval(), 3)}
        """


class SNA_Node_ListRemove(ScriptingBaseNode, bpy.types.Node):
    """Remove the first occurrence of an item from a list"""

    bl_idname = "SNA_Node_ListRemove"
    bl_label = "List Remove"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingDataSocket", "Item")
        self.add_output("ScriptingProgramSocket")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        item_code = self.inputs["Item"].eval("None")
        self.code = f"""
            if {item_code} in {list_code}:
                {list_code}.remove({item_code})
            {indent(self.outputs[0].eval(), 3)}
        """


class SNA_Node_ListPop(ScriptingBaseNode, bpy.types.Node):
    """Remove and return an item at a specific index"""

    bl_idname = "SNA_Node_ListPop"
    bl_label = "List Pop"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingIntegerSocket", "Index")
        self.add_output("ScriptingProgramSocket")
        self.add_output("ScriptingDataSocket", "Item")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        index_code = self.inputs["Index"].eval("-1")
        self.code = f"""
            _pop_result_{self.id} = {list_code}.pop({index_code}) if {list_code} else None
            {indent(self.outputs[0].eval(), 3)}
        """
        self.outputs["Item"].code = f"_pop_result_{self.id}"


class SNA_Node_ListGetItem(ScriptingBaseNode, bpy.types.Node):
    """Get an item from a list at a specific index"""

    bl_idname = "SNA_Node_ListGetItem"
    bl_label = "List Get Item"

    def on_create(self):
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingIntegerSocket", "Index")
        self.add_output("ScriptingDataSocket", "Item")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        index_code = self.inputs["Index"].eval("0")
        self.outputs["Item"].code = (
            f"({list_code}[{index_code}] if len({list_code}) > {index_code} else None)"
        )


class SNA_Node_ListSetItem(ScriptingBaseNode, bpy.types.Node):
    """Set an item in a list at a specific index"""

    bl_idname = "SNA_Node_ListSetItem"
    bl_label = "List Set Item"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingIntegerSocket", "Index")
        self.add_input("ScriptingDataSocket", "Item")
        self.add_output("ScriptingProgramSocket")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        index_code = self.inputs["Index"].eval("0")
        item_code = self.inputs["Item"].eval("None")
        self.code = f"""
            if len({list_code}) > {index_code}:
                {list_code}[{index_code}] = {item_code}
            {indent(self.outputs[0].eval(), 3)}
        """


class SNA_Node_ListLength(ScriptingBaseNode, bpy.types.Node):
    """Get the length of a list"""

    bl_idname = "SNA_Node_ListLength"
    bl_label = "List Length"

    def on_create(self):
        self.add_input("ScriptingListSocket", "List")
        self.add_output("ScriptingIntegerSocket", "Length")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        self.outputs["Length"].code = f"len({list_code})"


class SNA_Node_ListClear(ScriptingBaseNode, bpy.types.Node):
    """Clear all items from a list"""

    bl_idname = "SNA_Node_ListClear"
    bl_label = "List Clear"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingListSocket", "List")
        self.add_output("ScriptingProgramSocket")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        self.code = f"""
            {list_code}.clear()
            {indent(self.outputs[0].eval(), 3)}
        """


class SNA_Node_ListIndex(ScriptingBaseNode, bpy.types.Node):
    """Find the index of an item in a list"""

    bl_idname = "SNA_Node_ListIndex"
    bl_label = "List Index"

    def on_create(self):
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingDataSocket", "Item")
        self.add_output("ScriptingIntegerSocket", "Index")
        self.add_output("ScriptingBooleanSocket", "Found")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        item_code = self.inputs["Item"].eval("None")
        self.outputs["Index"].code = (
            f"({list_code}.index({item_code}) if {item_code} in {list_code} else -1)"
        )
        self.outputs["Found"].code = f"({item_code} in {list_code})"


class SNA_Node_ListExtend(ScriptingBaseNode, bpy.types.Node):
    """Extend a list by appending all items from another list"""

    bl_idname = "SNA_Node_ListExtend"
    bl_label = "List Extend"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingListSocket", "Items")
        self.add_output("ScriptingProgramSocket")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        items_code = self.inputs["Items"].eval("[]")
        self.code = f"""
            {list_code}.extend({items_code})
            {indent(self.outputs[0].eval(), 3)}
        """


class SNA_Node_ListReverse(ScriptingBaseNode, bpy.types.Node):
    """Reverse a list in place"""

    bl_idname = "SNA_Node_ListReverse"
    bl_label = "List Reverse"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingListSocket", "List")
        self.add_output("ScriptingProgramSocket")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        self.code = f"""
            {list_code}.reverse()
            {indent(self.outputs[0].eval(), 3)}
        """


class SNA_Node_ListSort(ScriptingBaseNode, bpy.types.Node):
    """Sort a list in place"""

    bl_idname = "SNA_Node_ListSort"
    bl_label = "List Sort"

    def update_props(self, context):
        self._generate()

    reverse: bpy.props.BoolProperty(
        name="Reverse",
        description="Sort in descending order",
        default=False,
        update=update_props,
    )

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingListSocket", "List")
        self.add_output("ScriptingProgramSocket")

    def draw(self, context, layout):
        layout.prop(self, "reverse")

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        reverse_str = "True" if self.reverse else "False"
        self.code = f"""
            {list_code}.sort(reverse={reverse_str})
            {indent(self.outputs[0].eval(), 3)}
        """


class SNA_Node_ListContains(ScriptingBaseNode, bpy.types.Node):
    """Check if a list contains an item"""

    bl_idname = "SNA_Node_ListContains"
    bl_label = "List Contains"

    def on_create(self):
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingDataSocket", "Item")
        self.add_output("ScriptingBooleanSocket", "Contains")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        item_code = self.inputs["Item"].eval("None")
        self.outputs["Contains"].code = f"({item_code} in {list_code})"


class SNA_Node_ListSlice(ScriptingBaseNode, bpy.types.Node):
    """Get a slice of a list"""

    bl_idname = "SNA_Node_ListSlice"
    bl_label = "List Slice"

    def on_create(self):
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingIntegerSocket", "Start")
        self.add_input("ScriptingIntegerSocket", "End")
        self.add_output("ScriptingListSocket", "Slice")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        start_code = self.inputs["Start"].eval("0")
        end_code = self.inputs["End"].eval("None")
        self.outputs["Slice"].code = f"{list_code}[{start_code}:{end_code}]"


class SNA_Node_ForEachList(ScriptingBaseNode, bpy.types.Node):
    """Iterate over each item in a list"""

    bl_idname = "SNA_Node_ForEachList"
    bl_label = "For Each (List)"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingListSocket", "List")
        self.add_output("ScriptingProgramSocket", "Loop")
        self.add_output("ScriptingProgramSocket", "Done")
        self.add_output("ScriptingDataSocket", "Item")
        self.add_output("ScriptingIntegerSocket", "Index")

    def draw(self, context, layout):
        pass

    def generate(self):
        list_code = self.inputs["List"].eval("[]")
        loop_body = indent(self.outputs["Loop"].eval("pass"), 3)
        done_body = indent(self.outputs["Done"].eval(), 2)
        self.outputs["Item"].code = f"_item_{self.id}"
        self.outputs["Index"].code = f"_index_{self.id}"
        self.code = f"""
            for _index_{self.id}, _item_{self.id} in enumerate({list_code}):
                {loop_body}
            {done_body}
        """
