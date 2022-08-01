import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_StartDrawingNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_StartDrawingNode"
    bl_label = "Start Drawing"
    node_color = "PROGRAM"
    bl_width_default = 200    

    draw_type: bpy.props.EnumProperty(
        name="Draw Type",
        description="The type of drawing that should be started",
        items=[("POST_PIXEL", "2D", "Post Pixel"), ("POST_VIEW", "3D", "Post View"), ("BACKDROP", "Backdrop", "Backdrop for node editors")],
        default="POST_PIXEL",
        update=SN_ScriptingBaseNode._evaluate)

    def update_references(self, context):
        self.trigger_ref_update(self)
        self._evaluate(context)

    ref_SN_FunctionNode: bpy.props.StringProperty(name="Function",
                                            description="The function to run",
                                            update=update_references)

    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                    name="Function Node Tree",
                                    description="The node tree to select the function from",
                                    poll=SN_ScriptingBaseNode.ntree_poll,
                                    update=SN_ScriptingBaseNode._evaluate)

    def draw_space_items(self, context):
        items = []
        names = ["SpaceView3D", "SpaceNodeEditor", "SpaceClipEditor", "SpaceConsole", "SpaceDopeSheetEditor", "SpaceFileBrowser",
                "SpaceGraphEditor", "SpaceImageEditor", "SpaceInfo", "SpaceNLA", "SpaceOutliner", "SpacePreferences",
                "SpaceProperties", "SpaceSequenceEditor", "SpaceSpreadsheet", "SpaceTextEditor"]
        for name in names:
            items.append((name, name, name))
        return items
    
    draw_space: bpy.props.EnumProperty(name="Draw Space",
                            description="The space this operator can run in and the text is drawn in",
                            update=update_references,
                            items=draw_space_items)

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.ref_ntree = self.node_tree

    def draw_node(self, context, layout):
        layout.prop(self, "name")

        row = layout.row(align=True)
        parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
        row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
        subrow = row.row(align=True)
        subrow.enabled = self.ref_ntree != None
        subrow.prop_search(self, "ref_SN_FunctionNode", bpy.data.node_groups[parent_tree.name].node_collection("SN_FunctionNode"), "refs", text="")

        layout.prop(self, "draw_type")
        layout.prop(self, "draw_space", text="Space")
        
    def evaluate(self, context):
        func = None
        if self.ref_ntree and self.ref_SN_FunctionNode in self.ref_ntree.nodes:
            func = self.ref_ntree.nodes[self.ref_SN_FunctionNode]

            self.code_imperative = f"""
                handler_{self.static_uid} = []
            """

            self.code = f"""
                handler_{self.static_uid}.append(bpy.types.{self.draw_space}.draw_handler_add({func.func_name}, (), 'WINDOW', '{self.draw_type}'))
                {self.indent(self.outputs[0].python_value, 4)}
            """

            self.code_unregister = f"""
                if handler_{self.static_uid}:
                    bpy.types.{self.draw_space}.draw_handler_remove(handler_{self.static_uid}[0], 'WINDOW')
                    handler_{self.static_uid}.pop(0)
            """