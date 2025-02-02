from scripting_nodes.src.features.nodes.references.reference_properties import (
    SNA_NodeReference,
)
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_GetVariable(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_GetVariable"
    bl_label = "Get Variable"
    sn_reference_properties = {"var"}

    var: bpy.props.StringProperty(name="Variable")

    def draw(self, context, layout):
        layout.prop_search(self, "var", context.scene.sna, "references", text="")

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_output("ScriptingProgramSocket")
        self.add_output("ScriptingStringSocket", "Value")

    def on_ref_change(self, node):
        update_socket_type(self.outputs[1], node.data_type)
        self._generate()

    def generate(self):
        self.code = f"""
            {indent(self.outputs[0].eval(), 3)}
        """
        ref = bpy.context.scene.sna.references.get(self.var)
        if ref:
            self.outputs[1].code = f"var_{ref.node_id}"
