from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_OT_TriggerOperator(bpy.types.Operator):
    bl_idname = "sna.trigger_operator"
    bl_label = "Trigger Operator"
    bl_description = "Execute this operator node"

    node_id: bpy.props.StringProperty()

    def execute(self, context):
        for node in context.space_data.edit_tree.nodes:
            if getattr(node, "id", None) == self.node_id:

                execution_globals = globals().copy()
                execution_globals["bpy"] = bpy

                node._execute(execution_globals, locals())

                op_id = node.operator_name.replace(" ", "_").lower()
                getattr(bpy.ops.sna, op_id)("INVOKE_DEFAULT")

        return {"FINISHED"}


class SNA_Node_Operator(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Operator"
    bl_label = "Operator"
    sn_options = {"ROOT_NODE"}

    def update_operator_name(self, context):
        self._generate()

    operator_name: bpy.props.StringProperty(
        name="Name",
        description="The name of the operator",
        default="My Operator",
        update=update_operator_name,
    )

    def draw(self, context, layout):
        layout.prop(self, "operator_name", text="Name")
        row = layout.row()
        row.scale_y = 1.5
        op = row.operator(
            "sna.trigger_operator", text="Trigger Operator", icon="FILE_FOLDER"
        )
        op.node_id = self.id

    def on_create(self):
        self.add_output("ScriptingLogicSocket", "Logic")

    def generate(self):
        op_id = self.operator_name.replace(" ", "_").lower()

        self.code = f"""
            import bpy

            class SNA_OT_{self.id}(bpy.types.Operator):
                bl_idname = "sna.{op_id}"
                bl_label = "{self.operator_name}"
                bl_description = "{self.operator_name}"
                bl_options = {{'REGISTER', 'UNDO'}}

                @classmethod
                def poll(cls, context):
                    return True
                
                def execute(self, context):
                    {indent(self.outputs[0].eval("pass"), 5)}
                    return {{'FINISHED'}}
        """