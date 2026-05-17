from .....lib.utils.sockets.modify import update_socket_type
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_SetProperty(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_SetProperty"
    bl_label = "Set Property"
    sn_reference_properties = {"prop"}

    def _apply_target_visibility(self):
        # Class-body targets (Operator/Preferences) have a fixed access path,
        # so the Target input is meaningless - hide it from the node UI.
        target = self.resolve_reference("prop")
        register_on = getattr(target, "register_on", "") if target else ""
        self.inputs[1].enabled = register_on not in {"Operator", "Preferences"}

    def update_prop(self, context):
        target = self.resolve_reference("prop")
        if target and hasattr(target, "data_type"):
            update_socket_type(self.inputs[2], target.data_type)
        self._apply_target_visibility()
        self._generate()

    prop: bpy.props.StringProperty(name="Property", update=update_prop)

    def draw(self, context, layout):
        self.draw_reference_prop(layout, "prop")
        target = self.resolve_reference("prop")
        register_on = getattr(target, "register_on", "") if target else ""
        if register_on in {"Operator", "Preferences"}:
            return
        if not self.inputs[1].is_linked:
            layout.label(text="Connect a data target", icon="INFO")

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingBlendDataSocket", "Target")
        self.add_input("ScriptingStringSocket", "Value")
        self.add_output("ScriptingProgramSocket")

    def on_ref_change(self, node):
        if hasattr(node, "data_type"):
            update_socket_type(self.inputs[2], node.data_type)
        self._apply_target_visibility()
        self._generate()

    def generate(self):
        target = self.resolve_reference("prop")
        prop_name = getattr(target, "prop_name", "") if target else ""
        if not prop_name:
            self.code_inline = f"""
                {indent(self.outputs[0].eval(), 4)}
            """
            return

        # Class-body properties: ignore the Target input, use the fixed access
        # path. (You can technically assign to preferences from generated code,
        # though it's unusual - we don't try to prevent it.)
        register_on = getattr(target, "register_on", "")
        if register_on == "Operator":
            self.code_inline = f"""
                self.{prop_name} = {self.inputs[2].eval()}
                {indent(self.outputs[0].eval(), 4)}
            """
            return
        if register_on == "Preferences":
            self.code_inline = f"""
                bpy.context.preferences.addons[__package__].preferences.{prop_name} = {self.inputs[2].eval()}
                {indent(self.outputs[0].eval(), 4)}
            """
            return

        if self.inputs[1].is_linked:
            target_code = self.inputs[1].eval()
            self.code_inline = f"""
                {target_code}.{prop_name} = {self.inputs[2].eval()}
                {indent(self.outputs[0].eval(), 6)}
            """
        else:
            # No target connected - skip set and log
            self.code_inline = f"""
                print("Set Property: No data target connected for '{prop_name}'")
                {indent(self.outputs[0].eval(), 6)}
            """
