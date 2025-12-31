from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Trigger(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Trigger"
    bl_label = "Trigger"

    def draw(self, context, layout):
        if bpy.context.scene.sna.addon.force_production:
            box = layout.box()
            box.alert = True
            box.label(text="This node is disabled with force production on!")
        row = layout.row()
        row.scale_y = 1.5
        row.operator("sna.trigger_node", text="Trigger").node_id = self.id

    def on_create(self):
        self.add_output("ScriptingLogicSocket")

    def generate(self):
        self.code = f"""
            {indent(self.outputs[0].eval(), 3)}
        """


class SNA_OT_Trigger(bpy.types.Operator):
    bl_idname = "sna.trigger_node"
    bl_label = "Trigger"
    bl_description = "Trigger the node"

    node_id: bpy.props.StringProperty()

    def execute(self, context):
        for node in context.space_data.edit_tree.nodes:
            if getattr(node, "id", None) == self.node_id:
                node._execute(globals(), locals())
        return {"FINISHED"}
