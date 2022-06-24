import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_DisplaySerpensShortcutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplaySerpensShortcutNode"
    bl_label = "Display Serpens Shortcut (Legacy)"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label")
        
    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                    name="Panel Node Tree",
                                    description="The node tree to select the panel from",
                                    poll=SN_ScriptingBaseNode.ntree_poll,
                                    update=SN_ScriptingBaseNode._evaluate)
        
    ref_SN_OnKeypressNode: bpy.props.StringProperty(name="Shortcut",
                                                description="The shortcut to display",
                                                update=SN_ScriptingBaseNode._evaluate)

    def evaluate(self, context):
        if self.ref_ntree and self.ref_SN_OnKeypressNode in self.ref_ntree.nodes:
            self.code_imperative = """
                def find_user_keyconfig(key):
                    km, kmi = addon_keymaps[key]
                    for item in bpy.context.window_manager.keyconfigs.user.keymaps[km.name].keymap_items:
                        found_item = False
                        if kmi.idname == item.idname:
                            found_item = True
                            for name in dir(kmi.properties):
                                if not name in ["bl_rna", "rna_type"] and not name[0] == "_":
                                    if not kmi.properties[name] == item.properties[name]:
                                        found_item = False
                        if found_item:
                            return item
                    print(f"Couldn't find keymap item for {key}, using addon keymap instead. This won't be saved across sessions!")
                    return kmi
            """
            node = self.ref_ntree.nodes[self.ref_SN_OnKeypressNode]
            src = f"find_user_keyconfig('{node.static_uid}')"
            self.code = f"{self.active_layout}.prop({src}, 'type', text={self.inputs['Label'].python_value}, full_event=True)"

    def draw_node(self, context, layout):
        row = layout.row(align=True)

        parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
        row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
        subrow = row.row(align=True)
        subrow.enabled = self.ref_ntree != None
        subrow.prop_search(self, "ref_SN_OnKeypressNode", parent_tree.node_collection("SN_OnKeypressNode"), "refs", text="")

        layout.label(text="Copy blender shortcuts from the blend data browser in display property", icon="INFO")