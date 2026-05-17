from ......lib.utils.code.format import indent
from ....base_node import ScriptingBaseNode
import bpy


class SNA_Node_CollectionClear(ScriptingBaseNode, bpy.types.Node):
    """Remove all items from a Blender CollectionProperty."""

    bl_idname = "SNA_Node_CollectionClear"
    bl_label = "Collection Clear"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingBlendDataSocket", "Collection")
        self.add_output("ScriptingProgramSocket")

    def generate(self):
        collection_code = self.inputs["Collection"].eval("None")
        next_code = indent(self.outputs[0].eval(), 3)

        self.code_inline = f"""
            {collection_code}.clear()
            {next_code}
        """
