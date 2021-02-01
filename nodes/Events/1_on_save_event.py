import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup
from ...compiler.compiler import get_module



class SN_OT_RunEventFunction(bpy.types.Operator):
    bl_idname = "sn.test_event"
    bl_label = "Test Event Function"
    bl_description = "Runs this event function"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    node: bpy.props.StringProperty()
    func_name: bpy.props.StringProperty()

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        module = get_module(node.addon_tree)
        if self.func_name in dir(module):
            exec("module."+self.func_name+"(None)")
        return {"FINISHED"}




class SN_OnSaveNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_OnSaveNode"
    bl_label = "On Save"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
    }

    action: bpy.props.EnumProperty(items=[("save_pre", "Before", "On saving a blend file (before)"), ("save_post", "After", "On saving a blend file (after)")],name="Time of Action", description="When you want your event handler to run", update=SN_ScriptingBaseNode.auto_compile)

    def on_create(self,context):
        self.add_execute_output("On Save")


    def draw_node(self,context,layout):
        row = layout.row()
        row.scale_y = 1.2
        row.enabled = get_module(self.addon_tree) != None
        op = row.operator("sn.test_event",text="Run Event",icon="PLAY")
        op.node = self.name
        op.func_name = f"{self.action}_handler_{self.uid}"
        layout.prop(self, "action", expand=True)


    def code_imports(self, context):
        return {
            "code": f"""
                    from bpy.app.handlers import persistent
                    """
        }


    def code_imperative(self, context):
        return {
            "code": f"""
                    @persistent
                    def {self.action}_handler_{self.uid}(dummy):
                        {self.outputs[0].code(6) if self.outputs[0].code().strip() else "pass"}
                    """
        }

    
    def code_register(self, context):
        return {
            "code": f"""
                    bpy.app.handlers.{self.action}.append({self.action}_handler_{self.uid})
                    """
        }


    def code_unregister(self, context):
        return {
            "code": f"""
                    bpy.app.handlers.{self.action}.remove({self.action}_handler_{self.uid})
                    """
        }