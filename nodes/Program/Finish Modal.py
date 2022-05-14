import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ReturnModalNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ReturnModalNode"
    bl_label = "Return Modal Operator"
    node_color = "PROGRAM"
    
    return_type: bpy.props.EnumProperty(name="Return Type",
                            description="The way this modal should be finished",
                            items=[("FINISHED", "Finish", "End the modal"),
                                   ("PASS_THROUGH", "Interactive", "Keep the modal running and let the events be used by other operators"),
                                   ("RUNNING_MODAL", "Not Interactive", "Keep the modal running but block other uses of the event")],
                            default="FINISHED",
                            update=SN_ScriptingBaseNode._evaluate)

    def on_create(self, context):
        self.add_execute_input()
        
    def draw_node(self, context, layout):
        col = layout.column()
        col.prop(self, "return_type", expand=True)
    
    def evaluate(self, context):
        self.code = f"""
        if event.type in ['RIGHTMOUSE', 'ESC']:
            return {{'CANCELLED'}}
        return {{"{self.return_type}"}}
        """