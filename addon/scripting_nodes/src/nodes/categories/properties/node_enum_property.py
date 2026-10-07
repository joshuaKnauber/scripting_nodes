"""Enum Property: a dropdown of items.

Items are either
  - STATIC: the items listed on the node, or a list connected to Items
    (`[(identifier, name, description), ...]`), stored in a module variable
  - DYNAMIC: a function Blender calls whenever it needs the items. The Update
    Items flow runs first (fill a Global Variable there), then the function
    returns that variable's value.
"""

import bpy

from ....core.context import NodeError
from ....core.naming import function_name
from ....lib.trees import node_by_id
from ....sockets.spec import BlendData, List, Logic
from ._property_base import PropertyNode

GLOBAL_VARIABLE_NODES = ("SNA_Node_GlobalVariable",)


def _item_changed(self, context):
    """Rebuild the enum node an item belongs to."""
    pointer = self.as_pointer()
    for node in getattr(self.id_data, "nodes", ()):
        for item in getattr(node, "enum_items", ()):
            if item.as_pointer() == pointer:
                node.mark_dirty()
                return


class SNA_EnumPropertyItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="Item", update=_item_changed)
    description: bpy.props.StringProperty(name="Description", update=_item_changed)


class SNA_OT_EnumPropertyAddItem(bpy.types.Operator):
    """Add an item"""

    bl_idname = "sna.enum_property_add_item"
    bl_label = "Add Item"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()

    def execute(self, context):
        node = node_by_id(self.node_id)
        if node is None or not hasattr(node, "enum_items"):
            return {"CANCELLED"}
        names = {item.name for item in node.enum_items}
        item = node.enum_items.add()
        i = len(node.enum_items)
        while f"Item {i}" in names:
            i += 1
        item.name = f"Item {i}"
        node.mark_dirty()
        return {"FINISHED"}


class SNA_OT_EnumPropertyRemoveItem(bpy.types.Operator):
    """Remove this item"""

    bl_idname = "sna.enum_property_remove_item"
    bl_label = "Remove Item"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        node = node_by_id(self.node_id)
        if node is None or not hasattr(node, "enum_items"):
            return {"CANCELLED"}
        if 0 <= self.index < len(node.enum_items):
            node.enum_items.remove(self.index)
            node.mark_dirty()
        return {"FINISHED"}


class SNA_Node_EnumProperty(PropertyNode, bpy.types.Node):
    bl_idname = "SNA_Node_EnumProperty"
    bl_label = "Enum Property"
    bpy_type = "EnumProperty"
    data_type = "ScriptingStringSocket"
    supported_options = PropertyNode.supported_options + ("ENUM_FLAG",)
    sn_reference_properties = {"items_variable": GLOBAL_VARIABLE_NODES}

    prop_label: bpy.props.StringProperty(name="Label", default="My Enum")
    prop_default: bpy.props.StringProperty(
        name="Default", description="Identifier of the default item"
    )
    items_mode: bpy.props.EnumProperty(
        name="Items Mode",
        items=[
            ("STATIC", "Static", "Items listed on the node or connected as a list"),
            ("DYNAMIC", "Dynamic", "Items from a global variable, updated by a flow"),
        ],
        default="STATIC",
    )
    enum_items: bpy.props.CollectionProperty(type=SNA_EnumPropertyItem)
    items_variable: bpy.props.StringProperty(
        name="Items Variable", description="Global variable holding the items list"
    )
    option_enum_flag: bpy.props.BoolProperty(
        name="Enum Flag", description="Allow selecting several items (a set)"
    )

    def on_create(self):
        for name in ("Option A", "Option B"):
            self.enum_items.add().name = name

    def socket_specs(self):
        static = self.items_mode == "STATIC"
        inputs = [List("items", "Items", enabled=static)]
        outputs = [
            Logic("on_update", "On Update"),
            BlendData("update_source", "Update Source"),
            Logic("update_items", "Update Items", enabled=not static),
        ]
        return inputs, outputs

    # -- code -----------------------------------------------------------------

    def items_name(self):
        return function_name(self, "enum_items")

    def get_items_name(self):
        return function_name(self, "get_items")

    def option_flags(self):
        return {**super().option_flags(), "ENUM_FLAG": self.option_enum_flag}

    def _default_arg(self):
        if not self.prop_default or self.items_mode == "DYNAMIC":
            return []  # dynamic enums only take an index as default
        if self.option_enum_flag:
            return [f"default={{{self.prop_default!r}}}"]
        return [f"default={self.prop_default!r}"]

    def property_args(self, ctx):
        if self.items_mode == "DYNAMIC":
            items = ctx.symbol(self, self.get_items_name())
        else:
            items = ctx.symbol(self, self.items_name())
        return [f"items={items}"] + self._default_arg()

    def _static_items(self, ctx):
        if ctx.is_linked("items"):
            return ctx.input("items")
        names = [item.name for item in self.enum_items]
        if self.prop_default and self.prop_default not in names:
            raise NodeError(f"Default '{self.prop_default}' isn't one of the items")
        if len(set(names)) != len(names):
            raise NodeError("Item names must be unique")
        items = [
            f"({item.name!r}, {item.name!r}, {item.description!r})"
            for item in self.enum_items
        ]
        if not items:
            return "[]"
        return "[\n    " + ",\n    ".join(items) + ",\n]"

    def emit(self, ctx):
        if self.items_mode == "STATIC":
            ctx.module(f"{self.items_name()} = {self._static_items(ctx)}")
        else:
            variable = ctx.resolve("items_variable")
            if variable is None:
                raise NodeError("Pick the global variable that holds the items")
            getter = ctx.symbol(variable, variable.getter_name())
            ctx.module(f"""
                def {self.get_items_name()}(self, context):
                    {ctx.flow("update_items")}
                    return {getter}()
            """)
        super().emit(ctx)

    # -- UI -------------------------------------------------------------------

    def draw_node(self, context, layout):
        layout.prop(self, "items_mode", text="")
        if self.items_mode == "DYNAMIC":
            self.draw_reference_prop(layout, "items_variable", text="Items")
            return
        if self.socket("items") and self.socket("items").is_linked:
            return
        col = layout.column(align=True)
        for i, item in enumerate(self.enum_items):
            row = col.row(align=True)
            row.prop(item, "name", text="")
            op = row.operator("sna.enum_property_remove_item", text="", icon="X")
            op.node_id = self.id
            op.index = i
        col.operator(
            "sna.enum_property_add_item", text="Add Item", icon="ADD"
        ).node_id = self.id

    def draw_settings(self, layout):
        layout.prop(self, "prop_default", text="Default Identifier")
        if self.items_mode == "STATIC" and len(self.enum_items):
            col = layout.column(align=True)
            col.label(text="Item Descriptions")
            for item in self.enum_items:
                col.prop(item, "description", text=item.name)
        layout.prop(self, "option_enum_flag")
