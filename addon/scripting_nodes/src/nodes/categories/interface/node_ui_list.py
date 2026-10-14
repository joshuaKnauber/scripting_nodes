"""UI List: Blender's list widget (layout.template_list) for a collection,
with an Integer property holding the selected item's index. Each row draws
the Item flow; the list filters and sorts by name on its own."""

import bpy

from ....blend_data.rna import blend_data_spec
from ....core import naming
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

    def emit_module(self, ctx):
        values = {"item_data": "item", "index": "index"}
        if ctx.is_linked("item"):
            row = ctx.flow("item", layout="layout", outputs=values)
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
                bl_idname = {name!r}

                def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
                    {ctx.join([row])}
        """)

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
            f"rows={ctx.input('rows')}",
        ]
        ctx.code(f"""
            {ctx.layout}.template_list({", ".join(args)})
            {ctx.flow("next")}
        """)
