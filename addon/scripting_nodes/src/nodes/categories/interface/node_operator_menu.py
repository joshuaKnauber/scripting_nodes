"""Operator Menu: one button per item of an operator's enum property, as a
dropdown (layout.operator_menu_enum) or a row (layout.operator_enum)."""

import bpy

from ....core import properties
from ....core.context import NodeError
from ....sockets.spec import Icon, Interface, String
from ..._icon import icon_argument
from ..._operator_call import OperatorCallMixin, _operator_rna
from ...base_node import ScriptingBaseNode


def enum_properties(node):
    """Names of the picked operator's enum properties."""
    if node.mode == "CUSTOM":
        target = node.resolve_reference("operator_sn")
        if target is None:
            return []
        names = properties.python_names(target.properties)
        return [
            names[p.id]
            for p in target.properties
            if p.property_type == "ENUM" and not p.enum_flag
        ]
    rna = _operator_rna(node.operator_idname())
    if rna is None:
        return []
    return [
        p.identifier
        for p in rna.properties
        if p.type == "ENUM" and not p.is_enum_flag and not p.is_hidden
    ]


def _search_properties(self, context, edit_text):
    return enum_properties(self)


class SNA_Node_OperatorMenu(OperatorCallMixin, ScriptingBaseNode, bpy.types.Node):
    """Buttons running an operator once per item of one of its enum
    properties: a dropdown, or a row of buttons."""

    bl_idname = "SNA_Node_OperatorMenu"
    bl_label = "Operator Menu"
    bl_width_default = 200

    enum_property: bpy.props.StringProperty(
        name="Property",
        description="The operator's enum property with the items",
        search=_search_properties,
    )
    style: bpy.props.EnumProperty(
        name="Style",
        items=[
            ("DROPDOWN", "Dropdown", "A dropdown with one entry per item"),
            ("BUTTONS", "Buttons", "One button per item"),
        ],
    )

    def socket_specs(self):
        inputs = [Interface()]
        if self.style == "DROPDOWN":
            inputs += [String("label", "Label"), Icon()]
        return inputs, [Interface("next")]

    def draw(self, context, layout):
        self.draw_operator_picker(layout)
        row = layout.row()
        row.alert = bool(self.enum_property) and (
            self.enum_property not in enum_properties(self)
        )
        row.prop(self, "enum_property", text="", icon="PRESET")
        layout.prop(self, "style", expand=True)

    def emit(self, ctx):
        idname = self.operator_idname()
        if not idname:
            raise NodeError("Pick an operator")
        if self.enum_property not in enum_properties(self):
            raise NodeError("Pick one of the operator's enum properties")
        args = [repr(idname), repr(self.enum_property)]
        if self.style == "DROPDOWN":
            args.append(f"text={ctx.input('label')}")
            icon = icon_argument(ctx)
            if icon:
                args.append(icon)
            call = "operator_menu_enum"
        else:
            call = "operator_enum"
        ctx.code(f"""
            {ctx.layout}.{call}({", ".join(args)})
            {ctx.flow("next")}
        """)
