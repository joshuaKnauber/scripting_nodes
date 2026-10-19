"""The node API for node packages: what their node files get with

    from . import sn

(the index files of an installed package pass it down, core/node_packages.py).
Everything here is public: packages written against `API_VERSION` keep
working until it changes. Add to it freely, remove or change only with a new
`API_VERSION`.

    class MY_Node_Slugify(sn.ScriptingBaseNode, bpy.types.Node):
        bl_idname = "MY_Node_Slugify"
        bl_label = "Slugify"
        sn_inputs = [sn.String("text", "Text")]
        sn_outputs = [sn.String("slug", "Slug")]

        def emit(self, ctx):
            ctx.output("slug", f"{ctx.input('text')}.lower().replace(' ', '-')")

`ctx` is documented in website/content/docs/development/context-reference.mdx.
"""

from .core.context import NodeError
from .core.naming import Class, Idname, Symbol
from .core.references import Reference
from .nodes.base_node import ScriptingBaseNode
from .sockets.spec import (
    BlendData,
    Boolean,
    Color,
    Data,
    Float,
    Flow,
    Icon,
    Integer,
    Interface,
    List,
    Logic,
    Socket,
    String,
    Vector,
)

API_VERSION = 1

__all__ = [
    "API_VERSION",
    "BlendData",
    "Boolean",
    "Class",
    "Color",
    "Data",
    "Float",
    "Flow",
    "Icon",
    "Idname",
    "Integer",
    "Interface",
    "List",
    "Logic",
    "NodeError",
    "Reference",
    "ScriptingBaseNode",
    "Socket",
    "String",
    "Symbol",
    "Vector",
]
