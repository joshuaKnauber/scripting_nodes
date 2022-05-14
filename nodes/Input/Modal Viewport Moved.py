import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ModalViewportMovedNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ModalViewportMovedNode"
    bl_label = "Modal Viewport Moved"
    node_color = "DEFAULT"

    def on_create(self, context):
        self.add_boolean_output("Viewport Moved")
        
    def draw_node(self, context, layout):
        for node in self.root_nodes:
            if node.bl_idname == "SN_ModalOperatorNode":
                break
        else:
            row = layout.row()
            row.alert = True
            row.label(text="This node only works with modal operators!", icon="ERROR")

    def evaluate(self, context):
        self.outputs[0].python_value = f"('WHEEL' in event.type)"