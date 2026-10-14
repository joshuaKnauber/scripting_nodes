"""Custom properties (`data["name"]`): values stored on Blender data without
registering a property, e.g. by other add-ons or the Custom Properties
panel. Since Blender 5.0 these don't reach registered properties
(`bpy.props`): use Get / Set Property for those."""

import bpy

from .....sockets.spec import BlendData, Boolean, Data, Flow, String
from ....base_node import ScriptingBaseNode


class SNA_Node_GetCustomProperty(ScriptingBaseNode, bpy.types.Node):
    """The value of a custom property, Default if it doesn't exist."""

    bl_idname = "SNA_Node_GetCustomProperty"
    bl_label = "Get Custom Property"
    sn_inputs = [
        BlendData("data", "Data"),
        String("name", "Name"),
        Data("default", "Default"),
    ]
    sn_outputs = [Data("value", "Value"), Boolean("exists", "Exists")]

    def emit(self, ctx):
        data, name = ctx.input("data"), ctx.input("name")
        ctx.output("value", f"{data}.get({name}, {ctx.input('default')})")
        ctx.output("exists", f"{name} in {data}")


class SNA_Node_SetCustomProperty(ScriptingBaseNode, bpy.types.Node):
    """Set a custom property (created if it doesn't exist), or remove it."""

    bl_idname = "SNA_Node_SetCustomProperty"
    bl_label = "Set Custom Property"
    sn_header_props = ("operation",)

    operation: bpy.props.EnumProperty(
        name="Operation",
        items=[
            ("SET", "Set", "Set the value, create the property if needed"),
            ("REMOVE", "Remove", "Remove the property if it exists"),
        ],
    )

    def socket_specs(self):
        inputs = [
            Flow(),
            BlendData("data", "Data"),
            String("name", "Name"),
            Data("value", "Value", enabled=self.operation == "SET"),
        ]
        return inputs, [Flow("next")]

    def emit(self, ctx):
        data, name = ctx.input("data"), ctx.input("name")
        if self.operation == "REMOVE":
            statement = f"{data}.pop({name}, None)"
        else:
            statement = f"{data}[{name}] = {ctx.input('value')}"
        ctx.code(f"""
            {statement}
            {ctx.flow("next")}
        """)
