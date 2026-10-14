"""Attributes by name (getattr / setattr), for names only known when the
add-on runs."""

import bpy

from .....sockets.spec import Boolean, Data, Flow, String
from ....base_node import ScriptingBaseNode


class SNA_Node_GetAttribute(ScriptingBaseNode, bpy.types.Node):
    """An attribute of any value by its name (`getattr`), Default if it has
    none. For names known in advance, Blender Data paths are simpler."""

    bl_idname = "SNA_Node_GetAttribute"
    bl_label = "Get Attribute"
    sn_inputs = [
        Data("data", "Data"),
        String("name", "Name"),
        Data("default", "Default"),
    ]
    sn_outputs = [Data("value", "Value"), Boolean("exists", "Exists")]

    def emit(self, ctx):
        data, name = ctx.input("data"), ctx.input("name")
        ctx.output("value", f"getattr({data}, {name}, {ctx.input('default')})")
        ctx.output("exists", f"hasattr({data}, {name})")


class SNA_Node_SetAttribute(ScriptingBaseNode, bpy.types.Node):
    """Set an attribute of any value by its name (`setattr`)."""

    bl_idname = "SNA_Node_SetAttribute"
    bl_label = "Set Attribute"
    sn_inputs = [
        Flow(),
        Data("data", "Data"),
        String("name", "Name"),
        Data("value", "Value"),
    ]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        data, name = ctx.input("data"), ctx.input("name")
        ctx.code(f"""
            setattr({data}, {name}, {ctx.input("value")})
            {ctx.flow("next")}
        """)
