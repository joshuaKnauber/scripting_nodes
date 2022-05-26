import operator
import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_OT_TriggerTriggerNode(bpy.types.Operator):
    bl_idname = "sn.trigger_trigger_node"
    bl_label = "Trigger Node"
    bl_description = "Trigger this node"
    bl_options = {"REGISTER", "INTERNAL"}
    
    uid: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        if self.uid in context.scene.sn.function_store:
            context.scene.sn.function_store[self.uid]()
        else:
            self.report({"WARNING"}, message="Couldn't find trigger function!")
        return {"FINISHED"}




class SN_TriggerNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_TriggerNode"
    bl_label = "Trigger"
    is_trigger = True
    bl_width_default = 200

    def on_create(self, context):
        self.add_execute_output()


    def draw_node(self,context,layout):
        row = layout.row()
        row.scale_y = 1.2
        op = row.operator("sn.trigger_trigger_node", text="Run Trigger", icon="PLAY")
        op.uid = self.static_uid


    @property
    def handler_name(self):
        return f"trigger_handler_{self.static_uid}"

    def evaluate(self, context):
        self.code = f"""
                        def {self.handler_name}():
                            {self.indent(self.outputs[0].python_value, 7) if self.outputs[0].python_value.strip() else 'pass'}
                        """
        self.code_register = f"bpy.context.scene.sn.function_store['{self.static_uid}'] = {self.handler_name}"
                        
    def evaluate_export(self, context):
        self.code = ""
        self.code_register = ""