from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_GetProperty(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_GetProperty"
    bl_label = "Get Property"
    sn_reference_properties = {"prop"}

    def update_prop(self, context):
        ref = bpy.context.scene.sna.references.get(self.prop)
        if ref and ref.node and hasattr(ref.node, "data_type"):
            update_socket_type(self.outputs[1], ref.node.data_type)
        self._generate()

    prop: bpy.props.StringProperty(name="Property", update=update_prop)

    def draw(self, context, layout):
        layout.prop_search(self, "prop", context.scene.sna, "references", text="")
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
        self.code = f"""
            {indent(self.outputs[0].eval(), 3)}
        """
        ref = bpy.context.scene.sna.references.get(self.prop)
        if ref and ref.node:
            prop_name = getattr(ref.node, "prop_name", "")
            if prop_name:
                if self.inputs[1].is_linked:
                    source_code = self.inputs[1].eval()
                    self.outputs[1].code = f"{source_code}.{prop_name}"
                else:
                    # No source connected - return None and log
                    self.outputs[1].code = "None"
                    self.code = f"""
                        print("Get Property: No data source connected for '{prop_name}'")
                        {indent(self.outputs[0].eval(), 6)}
                    """
