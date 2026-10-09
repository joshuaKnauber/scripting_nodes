import bpy

from ....core import naming
from ....sockets.socket_types import DATA_SOCKET_ENUM_ITEMS
from ....sockets.spec import Socket
from ...base_node import ScriptingBaseNode


class SNA_Node_GlobalVariable(ScriptingBaseNode, bpy.types.Node):
    """A value shared by the whole addon. Read and change it with Get/Set
    Variable nodes (also from other trees)."""

    bl_idname = "SNA_Node_GlobalVariable"
    bl_label = "Global Variable"
    sn_root = True
    sn_order = 10
    sn_header_props = ("data_type",)

    data_type: bpy.props.EnumProperty(items=DATA_SOCKET_ENUM_ITEMS, name="Data Type")

    def socket_specs(self):
        return [Socket(self.data_type, "value", "Initial Value")], []

    def sn_names(self):
        name = naming.snake(naming.label(self, socket=None, fallback=self.name), "var")
        return [
            naming.Symbol("storage", f"_{name}"),
            naming.Symbol("getter", f"get_{name}"),
            naming.Symbol("setter", f"set_{name}"),
        ]

    def getter_name(self):
        return self.sn_name("getter")

    def setter_name(self):
        return self.sn_name("setter")

    def emit(self, ctx):
        storage = ctx.name("storage")
        ctx.module(f"""
            {storage} = {ctx.input("value")}


            def {self.getter_name()}():
                return {storage}


            def {self.setter_name()}(value):
                global {storage}
                {storage} = value
        """)
