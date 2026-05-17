from ......lib.utils.code.format import indent
from ....base_node import ScriptingBaseNode
import bpy


class SNA_Node_CollectionRemove(ScriptingBaseNode, bpy.types.Node):
    """Remove an item from a Blender CollectionProperty by index."""

    bl_idname = "SNA_Node_CollectionRemove"
    bl_label = "Collection Remove"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingBlendDataSocket", "Collection")
        self.add_input("ScriptingIntegerSocket", "Index")
        self.add_output("ScriptingProgramSocket")

    def generate(self):
        collection_code = self.inputs["Collection"].eval("None")
        index_code = self.inputs["Index"].eval("0")
        next_code = indent(self.outputs[0].eval(), 3)

        self.code_inline = f"""
            {collection_code}.remove({index_code})
            {next_code}
        """
