from .....lib.utils.sockets.modify import update_socket_type
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
from ..._reference_signatures import PROPERTY_NODES
from ..Interface.blend_data_mixin import BlendDataModeMixin
import bpy


class SNA_Node_GetProperty(
    BlendDataModeMixin, ScriptingBaseNode, bpy.types.Node
):
    bl_idname = "SNA_Node_GetProperty"
    bl_label = "Get Property"
    sn_reference_properties = {"prop": PROPERTY_NODES}

    def update_prop(self, context):
        target = self.resolve_reference("prop")
        if target and hasattr(target, "data_type"):
            update_socket_type(self.outputs["Value"], target.data_type)
        self.apply_class_body_socket_visibility()
        self._generate()

    # Mode properties from mixin
    mode: bpy.props.EnumProperty(
        name="Mode",
        items=BlendDataModeMixin.get_mode_items(),
        default="CUSTOM",
        update=BlendDataModeMixin.update_mode,
    )

    blend_data_path: bpy.props.StringProperty(default="")
    blend_prop_name: bpy.props.StringProperty(default="")
    needs_data_input: bpy.props.BoolProperty(default=False)

    prop: bpy.props.StringProperty(name="Property", update=update_prop)

    def draw(self, context, layout):
        self.draw_mode_toggle(layout, context)

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingBlendDataSocket", "Data")
        self.add_output("ScriptingProgramSocket")
        self.add_output("ScriptingStringSocket", "Value")

    def on_ref_change(self, node):
        if hasattr(node, "data_type"):
            update_socket_type(self.outputs["Value"], node.data_type)
        self.apply_class_body_socket_visibility()
        self._generate()

    def generate(self):
        next_code = indent(self.outputs[0].eval(), 3)
        self.code_inline = f"""
            {next_code}
        """

        data_code, prop_name, error = self.get_prop_data_and_name()

        if error:
            self.outputs["Value"].code = "None"
            self.code_inline = f"""
                print("Get Property: {error}")
                {indent(self.outputs[0].eval(), 6)}
            """
            return

        if not prop_name:
            self.outputs["Value"].code = "None"
            return

        self.outputs["Value"].code = f"{data_code}.{prop_name}"
