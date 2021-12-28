import bpy



registered_subpanels = []



def register_dummy_subpanel(ntree, node, panel):
    func_name  = f"sna_dummy_{panel.bl_rna.identifier}"
    label = getattr(panel, "bl_label", panel.bl_rna.identifier.replace('_PT_', ' ').replace('_', ' ').title())
    panel = f"""
def {func_name}(self, context):
    layout = self.layout
    row = layout.row()
    row.alert = True
    if "SNA_PT_" in "{panel.bl_rna.identifier}":
        row.label(text="Select this custom panel on the subpanel node", icon="ERROR")
    else:
        row.scale_y = 1.5
        op = row.operator("sn.pick_subpanel_location", text="Select {label}")
        op.node_tree = "{ntree}"
        op.node = "{node}"
        op.panel = "{panel.bl_rna.identifier}"
    
bpy.types.{panel.bl_rna.identifier}.append({func_name})
registered_subpanels.append([bpy.types.{panel.bl_rna.identifier}, {func_name}])
"""
    # 
    #register panel
    try: exec(panel, globals())
    except: pass
     


class SN_OT_ActivateSubpanelPicker(bpy.types.Operator):
    bl_idname = "sn.activate_subpanel_picker"
    bl_label = "Select Subpanel Location"
    bl_description = "Select the location of this subpanel in the Interface"
    bl_options = {"REGISTER", "INTERNAL"}

    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    allow_subpanels: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE", "HIDDEN"})

    @classmethod
    def poll(cls, context):
        return not context.scene.sn.picker_active

    def execute(self, context):
        # register panels
        for panel in bpy.types.Panel.__subclasses__():
            if not getattr(panel, "bl_parent_id", False) or self.allow_subpanels:
                register_dummy_subpanel(self.node_tree, self.node, panel)
        
        # redraw screen
        for area in context.screen.areas:
            area.tag_redraw()

        # set picker active
        context.scene.sn.picker_active = True
        return {"FINISHED"}
     


class SN_OT_PickSubpanelLocation(bpy.types.Operator):
    bl_idname = "sn.pick_subpanel_location"
    bl_label = "Pick Location"
    bl_description = "Pick this location to put the subpanel into"
    bl_options = {"REGISTER", "INTERNAL"}

    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    panel: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        # find node and set properties
        if self.node_tree in bpy.data.node_groups:
            ntree = bpy.data.node_groups[self.node_tree]
            if self.node in ntree.nodes:
                node = ntree.nodes[self.node]
                node.panel_parent = self.panel
                
                panel = getattr(bpy.types, self.panel)
                if hasattr(panel, "bl_space_type") and hasattr(node, "space"):
                    node.space = panel.bl_space_type
                if hasattr(panel, "bl_region_type") and hasattr(node, "region"):
                    node.region = panel.bl_region_type
                if hasattr(panel, "bl_context") and hasattr(node, "context"):
                    node.context = panel.bl_context
                else:
                    node.context = ""

        # unregister panels
        for panel in registered_subpanels:
            try: panel[0].remove(panel[1])
            except: pass

        # reset saves and picker
        registered_subpanels.clear()
        context.scene.sn.picker_active = False
        return {"FINISHED"}
