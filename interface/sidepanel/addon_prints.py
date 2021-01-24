import bpy



class SN_PT_AddonPrintPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonPrintPanel"
    bl_label = "Print"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 4

    @classmethod
    def poll(cls, context):
        if context.scene.sn.editing_addon != "NONE" and context.space_data.tree_type == "ScriptingNodesTree":
            return len(context.scene.sn.addon_tree().sn_graphs[0].prints) > 0
        return False
    
    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()
        addon_graph = addon_tree.sn_graphs[0]
        
        for item in addon_graph.prints:
            box = layout.box()
            row = box.row()
            col = row.column()
            lines = item.value.split(";;;")
            if len(lines) > 0:
                lines = lines[:-1]
                for line in lines:
                    if line.isspace(): line = "<" + str(len(line)) + " spaces>"
                    elif not line: line = "<empty>"
                    col.label(text=line)