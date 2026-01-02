from .....lib.utils.sockets.modify import update_socket_type
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_SetVariable(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_SetVariable"
    bl_label = "Set Variable"
    sn_reference_properties = {"var"}

    def update_var(self, context):
        ref = bpy.context.scene.sna.references.get(self.var)
        if ref and ref.node and hasattr(ref.node, "data_type"):
            update_socket_type(self.inputs[1], ref.node.data_type)
        self._generate()

    var: bpy.props.StringProperty(name="Variable", update=update_var)

    def draw(self, context, layout):
        layout.prop_search(self, "var", context.scene.sna, "references", text="")

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingDataSocket", "Value")
        self.add_output("ScriptingProgramSocket")

    def on_ref_change(self, node):
        update_socket_type(self.inputs[1], node.data_type)
        self._generate()

    def generate(self):
        ref = bpy.context.scene.sna.references.get(self.var)
        if ref:
            self.code = f"""
                var_{ref.node_id} = {self.inputs[1].eval()}
                {indent(self.outputs[0].eval(), 4)}
            """
        else:
            self.code = f"""
                {indent(self.outputs[0].eval(), 4)}
            """
