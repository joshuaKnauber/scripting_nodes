import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_EndDrawingNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_EndDrawingNode"
    bl_label = "End Drawing"
    node_color = "PROGRAM"
    bl_width_default = 200

    ref_SN_StartDrawingNode: bpy.props.StringProperty(name="Handler",
                                            description="The handler to stop",
                                            update=SN_ScriptingBaseNode._evaluate)

    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                    name="Handler Node Tree",
                                    description="The node tree to select the handler from",
                                    poll=SN_ScriptingBaseNode.ntree_poll,
                                    update=SN_ScriptingBaseNode._evaluate)

    def on_ref_update(self, node, data=None):
        self._evaluate(bpy.context)

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.ref_ntree = self.node_tree

    def draw_node(self, context, layout):
        row = layout.row(align=True)
        parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
        row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
        subrow = row.row(align=True)
        subrow.enabled = self.ref_ntree != None
        subrow.prop_search(self, "ref_SN_StartDrawingNode", bpy.data.node_groups[parent_tree.name].node_collection("SN_StartDrawingNode"), "refs", text="")
        
    def evaluate(self, context):
        handler = None
        if self.ref_ntree and self.ref_SN_StartDrawingNode in self.ref_ntree.nodes:
            handler = self.ref_ntree.nodes[self.ref_SN_StartDrawingNode]

            self.code = f"""
                if handler_{handler.static_uid}:
                    bpy.types.{handler.draw_space}.draw_handler_remove(handler_{handler.static_uid}[0], 'WINDOW')
                    handler_{handler.static_uid}.pop(0)
                {self.indent(self.outputs[0].python_value, 4)}
            """