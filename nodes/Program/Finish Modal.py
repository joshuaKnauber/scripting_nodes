from email.policy import default
import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyNode import PropertyNode
from ...utils import get_python_name, unique_collection_name



class SN_FinishModalNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyNode):

    bl_idname = "SN_FinishModalNode"
    bl_label = "Finish Modal Operator"
    node_color = "PROGRAM"

    def on_create(self, context):
        self.add_execute_input()
    
    def evaluate(self, context):
        self.code = """
        return {"FINISHED"}
        """