from ....base_node import ScriptingBaseNode
import bpy


class SNA_Node_CollectionGetItem(ScriptingBaseNode, bpy.types.Node):
    """Get an item from a Blender CollectionProperty by index."""

    bl_idname = "SNA_Node_CollectionGetItem"
    bl_label = "Collection Get Item"

    def on_create(self):
        self.add_input("ScriptingBlendDataSocket", "Collection")
        self.add_input("ScriptingIntegerSocket", "Index")
        self.add_output("ScriptingBlendDataSocket", "Item")

    def generate(self):
        collection_code = self.inputs["Collection"].eval("None")
        index_code = self.inputs["Index"].eval("0")
        self.outputs["Item"].code = f"{collection_code}[{index_code}]"
