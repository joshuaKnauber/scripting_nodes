from .....lib.utils.sockets.modify import update_socket_type
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
from ..._reference_signatures import VARIABLE_NODES
import bpy


class SNA_Node_GetVariable(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_GetVariable"
    bl_label = "Get Variable"
    sn_reference_properties = {"var": VARIABLE_NODES}

    def update_var(self, context):
        target = self.resolve_reference("var")
        if target and hasattr(target, "data_type"):
            update_socket_type(self.outputs[1], target.data_type)
        self._generate()

    var: bpy.props.StringProperty(name="Variable", update=update_var)

    def draw(self, context, layout):
        self.draw_reference_prop(layout, "var")

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_output("ScriptingProgramSocket")
        self.add_output("ScriptingDataSocket", "Value")

    def on_ref_change(self, node):
        update_socket_type(self.outputs[1], node.data_type)
        self._generate()

    def generate(self):
        self.code_inline = f"""
            {indent(self.outputs[0].eval(), 3)}
        """
        target = self.resolve_reference("var")
        if not target:
            return
        getter = f"get_var_{target.id}"
        if self.reference_is_cross_tree("var"):
            self.code_imports = (
                f"from .{target.id_data.module_name} import {getter}"
            )
        self.outputs[1].code = f"{getter}()"
