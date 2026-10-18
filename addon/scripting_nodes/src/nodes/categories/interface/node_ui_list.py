"""UI List: Blender's list widget (layout.template_list) for a collection,
with an Integer property holding the selected item's index. Each row draws
the Item flow. Its filter options (name, sorting) work as in Blender's own
lists; a Filter Function hides items on top of that."""

import bpy

from ....blend_data.rna import blend_data_spec
from ....core import functions, naming
from ....core.context import NodeError
from ....sockets.data.socket_blend_data import linked_rna_type
from ....sockets.spec import BlendData, Integer, Interface
from ..._property_target import PropertyTargetMixin
from ...base_node import ScriptingBaseNode


class SNA_Node_UIList(PropertyTargetMixin, ScriptingBaseNode, bpy.types.Node):
    """A list of a collection's items, like Blender's lists of materials or
    vertex groups. Active Index is the Integer property storing which item
    is selected. Item draws each row (the item's name without it)."""

    bl_idname = "SNA_Node_UIList"
    bl_label = "UI List"
    bl_width_default = 220
    sn_property_references = {"prop": "INTEGER"}
    blender_prop_types = {"INT"}

    filter_function: bpy.props.PointerProperty(
        type=bpy.types.NodeTree,
        name="Filter Function",
        description=(
            "Function getting an item and returning a Boolean: only items it "
            "returns True for are listed"
        ),
        poll=lambda self, tree: (
            tree.bl_idname == "ScriptingNodeTree" and functions.is_function(tree)
        ),
    )

    def socket_specs(self):
        item_type, _ = linked_rna_type(self.socket("items"))
        inputs = [
            Interface(),
            BlendData("items", "Items", collection=True),
            Integer("rows", "Rows", default=5),
            *self.target_input_specs(),
        ]
        outputs = [
            Interface("item", "Item"),
            Interface("next", "After"),
            blend_data_spec("item_data", "Item", item_type),
            Integer("index", "Index"),
        ]
        return inputs, outputs

    def sn_names(self):
        label = naming.label(self, socket=None, fallback="list")
        return [naming.Class("class", "UL", label)]

    def draw(self, context, layout):
        layout.label(text="Active Index", icon="LINENUMBERS_ON")
        self.draw_target(layout)
        layout.prop(self, "filter_function", text="", icon="FILTER")

    def emit_module(self, ctx):
        values = {"item_data": "item", "index": "index"}
        if ctx.is_linked("item"):
            row = ctx.flow("item", layout="layout", outputs=values, horizontal=True)
        else:
            row = """
                if isinstance(getattr(item, "name", None), str):
                    layout.prop(item, "name", text="", emboss=False, icon_value=icon)
                else:
                    layout.label(text=str(item))
            """
        name = ctx.name("class")
        ctx.module(f"""
            class {name}(bpy.types.UIList):
                def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
                    {ctx.join([row])}
                {ctx.join([self._filter_items(ctx)])}
        """)

    def _filter_items(self, ctx):
        """filter_items calling the Filter Function, keeping Blender's own
        name filter and sorting (they only work by default without it)."""
        tree = self.filter_function
        if tree is None:
            return ""
        problem = functions.problem(tree) if functions.is_function(tree) else ""
        if problem or not functions.is_function(tree):
            raise NodeError(problem or "The Filter Function isn't a function")
        if not functions.returns(tree):
            raise NodeError("The Filter Function has to return a Boolean")
        args = ["item"] if functions.parameters(tree) else []
        args += functions.scope_arguments(tree, {"self": "self", "context": "context"})
        call = f"{ctx.symbol(tree, tree.function_name)}({', '.join(args)})"
        if len(functions.returns(tree)) > 1:
            call += "[0]"
        return f"""
            def filter_items(self, context, data, property):
                items = getattr(data, property)
                lists = bpy.types.UI_UL_list
                flags = [self.bitflag_filter_item] * len(items)
                if self.filter_name:
                    flags = lists.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, "name")
                for i, item in enumerate(items):
                    if flags[i] and not {call}:
                        flags[i] = 0
                order = lists.sort_items_by_name(items, "name") if self.use_filter_sort_alpha else []
                return flags, order
        """

    def emit(self, ctx):
        if not ctx.is_linked("items"):
            raise NodeError("Connect the collection to list")
        items = ctx.input("items")
        owner, dot, attribute = items.rpartition(".")
        if not dot or not attribute.isidentifier():
            raise NodeError("Items needs a collection of Blender data or a property")
        data, index = self.property_target(ctx)
        args = [
            repr(ctx.name("class")),
            '""',
            owner,
            repr(attribute),
            data,
            repr(index),
            ctx.keyword("rows", "rows", 5),
        ]
        args = [arg for arg in args if arg]
        ctx.code(f"""
            {ctx.layout}.template_list({", ".join(args)})
            {ctx.flow("next")}
        """)
