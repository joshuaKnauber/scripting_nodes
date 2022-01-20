import bpy



registered_panels = []



def register_dummy_panel(ntree, node, space, region):
    idname  = f"SNA_PT_Dummy{space}{region}"

    panel = f"""
class {idname}(bpy.types.Panel):
    bl_label = "test"
    bl_space_type = '{space}'
    bl_region_type = '{region}'
    bl_category = 'SERPENS'
    bl_options = {{"HIDE_HEADER"}}
    bl_order = 0
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.5
        row.alert = True
        op = row.operator("sn.pick_panel_location", text="Select {space.replace("_", " ").title()} {region.replace("_", " ").title()}")
        op.node_tree = "{ntree}"
        op.node = "{node}"
        op.space = "{space}"
        op.region = "{region}"
        op.context = ""
        if hasattr(context.space_data, "context"):
            row = layout.row()
            row.scale_y = 1.5
            row.alert = True
            op = row.operator("sn.pick_panel_location", text="Select {space.replace("_", " ").title()} {region.replace("_", " ").title()} "+context.space_data.context.replace("_", " ").title())
            op.node_tree = "{ntree}"
            op.node = "{node}"
            op.space = "{space}"
            op.region = "{region}"
            op.context = context.space_data.context.lower()
    
bpy.utils.register_class({idname})
registered_panels.append({idname})
"""
    #register panel
    try: exec(panel, globals())
    except: pass
     


class SN_OT_ActivatePanelPicker(bpy.types.Operator):
    bl_idname = "sn.activate_panel_picker"
    bl_label = "Select Panel Location"
    bl_description = "Select the location of this panel in the Interface"
    bl_options = {"REGISTER", "INTERNAL"}

    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    @classmethod
    def poll(cls, context):
        return not context.scene.sn.picker_active

    def execute(self, context):
        # possible panel locations
        space_types = ["EMPTY", "VIEW_3D", "IMAGE_EDITOR", "NODE_EDITOR",
                        "SEQUENCE_EDITOR", "CLIP_EDITOR", "DOPESHEET_EDITOR",
                        "GRAPH_EDITOR", "NLA_EDITOR", "TEXT_EDITOR", "CONSOLE",
                        "INFO", "TOPBAR", "STATUSBAR", "OUTLINER", "PROPERTIES",
                        "FILE_BROWSER", "SPREADSHEET", "PREFERENCES"]
        region_types = ["WINDOW", "HEADER", "CHANNELS", "TEMPORARY", "UI", "TOOLS",
                        "TOOL_PROPS", "PREVIEW", "HUD", "NAVIGATION_BAR", "EXECUTE",
                        "FOOTER", "TOOL_HEADER", "XR"]

        # register panels
        registered_panels.clear()
        for space in space_types:
            for region in region_types:
                register_dummy_panel(self.node_tree, self.node, space, region)
        
        # redraw screen
        for area in context.screen.areas:
            area.tag_redraw()

        # set picker active
        context.scene.sn.picker_active = True
        return {"FINISHED"}
     


class SN_OT_PickPanelLocation(bpy.types.Operator):
    bl_idname = "sn.pick_panel_location"
    bl_label = "Pick Location"
    bl_description = "Pick this location to put the panel into"
    bl_options = {"REGISTER", "INTERNAL"}

    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    space: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    region: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    context: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        # find node and set properties
        if self.node_tree in bpy.data.node_groups:
            ntree = bpy.data.node_groups[self.node_tree]
            if self.node in ntree.nodes:
                node = ntree.nodes[self.node]
                node.space = self.space
                node.region = self.region
                node.context = self.context

        # unregister panels
        for panel in registered_panels:
            try: bpy.utils.unregister_class(panel)
            except: pass

        # reset saves and picker
        registered_panels.clear()
        context.scene.sn.picker_active = False
        return {"FINISHED"}
