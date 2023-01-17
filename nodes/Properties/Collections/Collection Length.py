import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_CollectionLengthNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_CollectionLengthNode"
    bl_label = "Collection Length"
    node_color = "PROPERTY"

    def on_create(self, context):
        self.add_collection_property_input()
        self.add_integer_output("Length")

    def evaluate(self, context):
        self.outputs[0].python_value = f"len({self.inputs[0].python_value})"