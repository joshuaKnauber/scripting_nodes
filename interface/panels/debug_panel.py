import bpy


class SN_PT_NodeTreeDebugPopover(bpy.types.Panel):
    bl_idname = "SN_PT_NodeTreeDebugPopover"
    bl_label = "Node Trees"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "HEADER"

    def draw(self, context):
        layout = self.layout
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                row = layout.row()
                row.prop(ntree, "show_debug", text="", icon="HIDE_OFF" if ntree.show_debug else "HIDE_ON", emboss=False)
                subrow = row.row()
                subrow.active = ntree.show_debug
                subrow.label(text=ntree.name)


class SN_PT_DebugPanel(bpy.types.Panel):
    bl_idname = "SN_PT_DebugPanel"
    bl_label = ""
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED", "HEADER_LAYOUT_EXPAND"}
    bl_order = 7

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree
    
    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.sn, "live_variable_debug", text="", invert_checkbox=context.scene.sn.live_variable_debug, icon="KEYTYPE_EXTREME_VEC" if context.scene.sn.live_variable_debug else "HANDLETYPE_FREE_VEC")
        layout.label(text="Variable State")
        layout.popover("SN_PT_NodeTreeDebugPopover", text="", icon="SCRIPT")

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        if sn.module_store:
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree":
                    if ntree.python_name in sn.module_store[0][0] and ntree.show_debug:
                        box = col.box()
                        subcol = box.column(align=True)
                        subcol.label(text=f"{ntree.name}:")
                        for var in sn.module_store[0][0][ntree.python_name]:
                            var_data = list(filter(lambda v: v.python_name == var, ntree.variables))
                            name = var if not var_data else var_data[0].name
                            row = subcol.row()
                            row.active = False
                            row.label(text=f"{name}:")
                            subcol.label(text=str(sn.module_store[0][0][ntree.python_name][var]))