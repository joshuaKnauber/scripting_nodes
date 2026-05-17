from .....lib.utils.sockets.modify import update_socket_type
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_GetProperty(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_GetProperty"
    bl_label = "Get Property"
    sn_reference_properties = {"prop"}

    def update_prop(self, context):
        target = self.resolve_reference("prop")
        if target and hasattr(target, "data_type"):
            update_socket_type(self.outputs[1], target.data_type)
        self._generate()

    prop: bpy.props.StringProperty(name="Property", update=update_prop)

    def draw(self, context, layout):
        self.draw_reference_prop(layout, "prop")
        if not self.inputs[1].is_linked:
            layout.label(text="Connect a data source", icon="INFO")

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingBlendDataSocket", "Source")
        self.add_output("ScriptingProgramSocket")
        self.add_output("ScriptingStringSocket", "Value")

    def on_ref_change(self, node):
        if hasattr(node, "data_type"):
            update_socket_type(self.outputs[1], node.data_type)
        self._generate()

    def generate(self):
        self.code_inline = f"""
            {indent(self.outputs[0].eval(), 3)}
        """
        target = self.resolve_reference("prop")
        if not target:
            return
        prop_name = getattr(target, "prop_name", "")
        if not prop_name:
            return
        if self.inputs[1].is_linked:
            source_code = self.inputs[1].eval()
            self.outputs[1].code = f"{source_code}.{prop_name}"
        else:
            # No source connected - return None and log
            self.outputs[1].code = "None"
            self.code_inline = f"""
                print("Get Property: No data source connected for '{prop_name}'")
                {indent(self.outputs[0].eval(), 6)}
            """
