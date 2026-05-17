from .....lib.utils.sockets.modify import update_socket_type
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_SetVariable(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_SetVariable"
    bl_label = "Set Variable"
    sn_reference_properties = {"var"}

    def update_var(self, context):
        target = self.resolve_reference("var")
        if target and hasattr(target, "data_type"):
            update_socket_type(self.inputs[1], target.data_type)
        self._generate()

    var: bpy.props.StringProperty(name="Variable", update=update_var)

    def draw(self, context, layout):
        self.draw_reference_prop(layout, "var")

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingDataSocket", "Value")
        self.add_output("ScriptingProgramSocket")

    def on_ref_change(self, node):
        update_socket_type(self.inputs[1], node.data_type)
        self._generate()

    def generate(self):
        target = self.resolve_reference("var")
        if not target:
            self.code_inline = f"""
                {indent(self.outputs[0].eval(), 4)}
            """
            return
        setter = f"set_var_{target.id}"
        if self.reference_is_cross_tree("var"):
            self.code_imports = (
                f"from .{target.id_data.module_name} import {setter}"
            )
        self.code_inline = f"""
            {setter}({self.inputs[1].eval()})
            {indent(self.outputs[0].eval(), 4)}
        """
