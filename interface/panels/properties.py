import bpy



class SN_PT_PropertyPanel(bpy.types.Panel):
    bl_idname = "SN_PT_PropertyPanel"
    bl_label = "Properties"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree
    
    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn
        
        # draw property ui list
        row = layout.row(align=False)
        row.template_list("SN_UL_PropertyList", "Properties", sn, "properties", sn, "property_index", rows=4)
        col = row.column(align=True)
        col.operator("sn.add_property", text="", icon="ADD")
        col.operator("sn.add_property", text="", icon="VIEWZOOM")
        col.operator("sn.remove_property", text="", icon="REMOVE")
        
        if sn.property_index < len(sn.properties):
            prop = sn.properties[sn.property_index]
            
            # draw property debug
            if sn.debug_python_properties:
                box = layout.box()
                col = box.column(align=True)
                row = col.row()
                row.enabled = False
                row.label(text="Register")
                for line in prop.register_code.split("\n"):
                    col.label(text=line)
                box = layout.box()
                col = box.column(align=True)
                row = col.row()
                row.enabled = False
                row.label(text="Unregister")
                for line in prop.unregister_code.split("\n"):
                    col.label(text=line)
            
            col = layout.column()
            col.use_property_split = True
            col.use_property_decorate = False

            # draw general property settings
            prop.draw(context, col)
            
            # draw property specific settings
            col.separator()
            prop.settings.draw(context, col, prop)