import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyNode import PropertyNode



class SN_OperatorNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyNode):

    bl_idname = "SN_OperatorNode"
    bl_label = "Operator"
    is_trigger = True
    bl_width_default = 200

    def on_create(self, context):
        self.add_boolean_input("Disable")
        self.add_execute_output("Execute")
        self.add_execute_output("Before Popup")

    def evaluate(self, context):
        pass
    
    def draw_node(self, context, layout):
        self.draw_list(layout)