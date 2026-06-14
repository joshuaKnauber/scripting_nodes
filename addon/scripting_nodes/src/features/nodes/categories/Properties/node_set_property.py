from .....lib.utils.sockets.modify import update_socket_type
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
from ..._reference_signatures import PROPERTY_NODES
from ..Interface.blend_data_mixin import BlendDataModeMixin
import bpy


class SNA_Node_SetProperty(
    BlendDataModeMixin, ScriptingBaseNode, bpy.types.Node
):
    bl_idname = "SNA_Node_SetProperty"
    bl_label = "Set Property"
    sn_reference_properties = {"prop": PROPERTY_NODES}

    def update_prop(self, context):
        target = self.resolve_reference("prop")
        if target and hasattr(target, "data_type"):
            update_socket_type(self.inputs["Value"], target.data_type)
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
        self.add_input("ScriptingStringSocket", "Value")
        self.add_output("ScriptingProgramSocket")

    def on_ref_change(self, node):
        if hasattr(node, "data_type"):
            update_socket_type(self.inputs["Value"], node.data_type)
        self.apply_class_body_socket_visibility()
        self._generate()

    def generate(self):
        data_code, prop_name, error = self.get_prop_data_and_name()
        next_code = indent(self.outputs[0].eval(), 4)

        if error:
            self.code_inline = f"""
                print("Set Property: {error}")
                {next_code}
            """
            return

        if not prop_name:
            self.code_inline = f"""
                {next_code}
            """
            return

        self.code_inline = f"""
            {data_code}.{prop_name} = {self.inputs["Value"].eval()}
            {next_code}
        """
