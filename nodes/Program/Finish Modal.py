import bpy
from ...utils import normalize_code
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
    
    enable_escape: bpy.props.BoolProperty(default=True,
                            name="Default Escape Modal Options",
                            description="Finish the modal automatically when pressing escape or rightclicking. If this is turned off you need to add a way to finish a modal yourself",
                            update=SN_ScriptingBaseNode._evaluate)

    def on_create(self, context):
        self.add_execute_input()
        
    def draw_node(self, context, layout):
        col = layout.column()
        col.prop(self, "return_type", expand=True)
        layout.prop(self, "enable_escape")
        
        for node in self.root_nodes:
            if node.bl_idname == "SN_ModalOperatorNode":
                break
        else:
            row = layout.row()
            row.alert = True
            row.label(text="This node only works with modal operators!", icon="ERROR")
    
    def evaluate(self, context):
        escape = """
        if event.type in ['RIGHTMOUSE', 'ESC']:
            self.execute(context)
            return {'CANCELLED'}
        """
        
        self.code = f"""
        {self.indent(normalize_code(escape), 2) if self.enable_escape else ""}
        {"self.execute(context)" if self.return_type == "FINISHED" else ""}
        return {{"{self.return_type}"}}
        """