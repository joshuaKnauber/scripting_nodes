from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_SetProperty(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_SetProperty"
    bl_label = "Set Property"
    sn_reference_properties = {"prop"}

    def update_prop(self, context):
        ref = bpy.context.scene.sna.references.get(self.prop)
        if ref and ref.node and hasattr(ref.node, "data_type"):
            update_socket_type(self.inputs[2], ref.node.data_type)
        self._generate()

    prop: bpy.props.StringProperty(name="Property", update=update_prop)

    def draw(self, context, layout):
        layout.prop_search(self, "prop", context.scene.sna, "references", text="")

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingBlendDataSocket", "Target")
        self.add_input("ScriptingStringSocket", "Value")
        self.add_output("ScriptingProgramSocket")

    def on_ref_change(self, node):
        if hasattr(node, "data_type"):
            update_socket_type(self.inputs[2], node.data_type)
        self._generate()

    def generate(self):
        ref = bpy.context.scene.sna.references.get(self.prop)
        if ref and ref.node:
            prop_name = getattr(ref.node, "prop_name", "")
            if prop_name:
                target_code = self.inputs[1].eval()
                self.code = f"""
                    {target_code}.{prop_name} = {self.inputs[2].eval()}
                    {indent(self.outputs[0].eval(), 5)}
                """
            else:
                self.code = f"""
                    {indent(self.outputs[0].eval(), 5)}
                """
        else:
            self.code = f"""
                {indent(self.outputs[0].eval(), 4)}
            """
