import bpy

from ....constants import sockets
from ....constants.properties import id_type_items, id_type_names
from ..base_node import SNA_BaseNode


class SNA_NodeBoolProperty(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeBoolProperty"
    bl_label = "Boolean Property"
    bl_width_default = 200

    source_type: bpy.props.EnumProperty(
        name="Source",
        description="The type of data this property should be attached to. When selecting e.g. 'Object', each object will have a value for this property. An example for this is the objects location.",
        items=id_type_items,
        default=id_type_names().index("Scene"),
        update=lambda self, _: self.mark_dirty(),
    )

    def on_create(self):
        self.name = "New Boolean"

        inp = self.add_input(sockets.EXECUTE, "Property Group")
        inp.make_disabled()
        # self.add_output(sockets.EXECUTE, "On Update")
        # self.add_output(sockets.PROPERTY, "Updated Property")
        # self.add_output(sockets.BOOLEAN, "Updated Value")

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        layout.separator()
        row = layout.row(align=True)
        row.scale_y = 1.2
        op = row.operator("sna.property_getter", text="Get", icon="SORT_DESC")
        op.node = self.id
        op.property_type = "BOOLEAN"
        op = row.operator("sna.property_getter", text="Set", icon="SORT_ASC")
        op.node = self.id
        op.property_type = "BOOLEAN"
        layout.separator(factor=0.6)
        row = layout.row()
        row.prop(self, "name", text="")
        row.operator(
            "sna.node_settings", text="", icon="PREFERENCES", emboss=False
        ).node = self.id
        layout.prop(self, "source_type", text="")

    def identifier(self):
        return f"prop_{self.id}"  # TODO better identifier

    def generate(self, context, trigger):
        has_group = (
            self.inputs["Property Group"].editable
            and self.inputs["Property Group"].has_next()
        )
        self.require_register = not has_group

        update = ""
        if self.outputs["On Update"].has_next():
            self.code = f"""
                def on_update_{self.identifier()}(self, context):
                    {self.outputs["On Update"].get_code(5, "pass")}
            """
            update = f", update=on_update_{self.identifier()}"

        self.outputs["Updated Property"].code = f"self.{self.identifier()}"
        self.outputs["Updated Property"].set_meta("parent", "self")
        self.outputs["Updated Property"].set_meta("identifier", self.identifier())
        self.outputs["Updated Property"].set_meta("type", self.source_type)

        self.outputs["Updated Value"].code = f"self.{self.identifier()}"

        self.code_register = f"bpy.types.{self.source_type}.{self.identifier()} = bpy.props.BoolProperty(name='{self.name}'{update})"
        self.code_unregister = f"del bpy.types.{self.source_type}.{self.identifier()}"
