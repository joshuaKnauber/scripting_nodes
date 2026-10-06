from ....base_node import ScriptingBaseNode
import bpy


class SNA_Node_CollectionLength(ScriptingBaseNode, bpy.types.Node):
    """Number of items in a Blender CollectionProperty."""

    bl_idname = "SNA_Node_CollectionLength"
    bl_label = "Collection Length"

    def on_create(self):
        self.add_input("ScriptingBlendDataSocket", "Collection")
        self.add_output("ScriptingIntegerSocket", "Length")

    def generate(self):
        collection_code = self.inputs["Collection"].eval("None")
        self.outputs["Length"].code = f"len({collection_code})"
