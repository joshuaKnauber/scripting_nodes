import bpy

from ....core import naming, properties
from ....core.context import NodeError
from ....sockets.spec import BlendData, Logic, Socket
from ...base_node import ScriptingBaseNode


class SNA_Node_OnPropertyUpdate(ScriptingBaseNode, bpy.types.Node):
    """Runs when a property of this add-on changes."""

    bl_idname = "SNA_Node_OnPropertyUpdate"
    bl_label = "On Property Update"
    bl_width_default = 200
    sn_root = True
    sn_property_references = {"prop": "UPDATE"}

    def target(self):
        return properties.find(self.prop_id)

    def socket_specs(self):
        found = self.target()
        value = Socket(
            properties.socket_type(found.prop) if found else "ScriptingDataSocket",
            "value",
            "Value",
        )
        if found:
            value.attrs.update(properties.socket_attrs(found.prop))
        return [], [Logic(), value, BlendData("owner", "Owner")]

    def sn_names(self):
        found = self.target()
        name = properties.python_name(found) if found else "property"
        return [naming.Symbol("function", f"on_{name}_update")]

    def draw(self, context, layout):
        layout.prop_search(
            self,
            "prop",
            context.scene.sna,
            properties.picker_attr("UPDATE"),
            text="",
        )

    def emit(self, ctx):
        found = self.target()
        if found is None:
            raise NodeError("Pick a property")
        if found.prop.property_type == "COLLECTION":
            raise NodeError("Collections have no update")
        name = properties.python_name(found)
        # an add-on property in the add-on's group: `self` is that group
        grouped = found.kind == "ADDON" and found.prop.in_addon_group
        values = {
            "value": f"self.{name}",
            "owner": "self.id_data" if grouped else "self",
        }
        ctx.module(f"""
            def {ctx.name("function")}(self, context):
                {ctx.flow("flow", outputs=values)}
        """)
