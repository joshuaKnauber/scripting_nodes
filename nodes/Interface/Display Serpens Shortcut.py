import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_DisplaySerpensShortcutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplaySerpensShortcutNode"
    bl_label = "Display Serpens Shortcut"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label")
        self.add_icon_input("Icon")
        
    src_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                    name="Panel Node Tree",
                                    description="The node tree to select the panel from",
                                    poll=SN_ScriptingBaseNode.ntree_poll,
                                    update=SN_ScriptingBaseNode._evaluate)
        
    ref_SN_OnKeypressNode: bpy.props.StringProperty(name="Shortcut",
                                                description="The shortcut to display",
                                                update=SN_ScriptingBaseNode._evaluate)

    def evaluate(self, context):
        self.code_imperative = ""
        src = ""
        self.code = f"{self.active_layout}.prop({src}, 'type', text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value}, full_event=True)"

    def draw_node(self, context, layout):
        row = layout.row(align=True)

        parent_tree = self.src_ntree if self.src_ntree else self.node_tree
        row.prop_search(self, "src_ntree", bpy.data, "node_groups", text="")
        subrow = row.row(align=True)
        subrow.enabled = self.src_ntree != None
        subrow.prop_search(self, "ref_SN_OnKeypressNode", parent_tree.node_collection("SN_OnKeypressNode"), "refs", text="")

        layout.label(text="Copy blender shortcuts from the blend data browser in display property", icon="INFO")