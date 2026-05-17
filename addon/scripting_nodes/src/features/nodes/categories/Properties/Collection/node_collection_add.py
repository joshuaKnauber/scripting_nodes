from ......lib.utils.code.format import indent
from ....base_node import ScriptingBaseNode
import bpy


class SNA_Node_CollectionAdd(ScriptingBaseNode, bpy.types.Node):
    """Append a new item to a Blender CollectionProperty and expose it."""

    bl_idname = "SNA_Node_CollectionAdd"
    bl_label = "Collection Add"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingBlendDataSocket", "Collection")
        self.add_output("ScriptingProgramSocket")
        self.add_output("ScriptingBlendDataSocket", "New Item")

    def generate(self):
        collection_code = self.inputs["Collection"].eval("None")
        next_code = indent(self.outputs[0].eval(), 3)

        # Bind the .add() return so downstream nodes can reference the new
        # item via the New Item output without re-calling .add().
        item_var = f"_sn_new_item_{self.id}"
        self.outputs["New Item"].code = item_var

        self.code_inline = f"""
            {item_var} = {collection_code}.add()
            {next_code}
        """
