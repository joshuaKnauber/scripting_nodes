import bpy
import re
from ...node_tree.base_node import SN_ScriptingBaseNode


panel_locations = []
panel_template = """
class SN_PT_SelectPanelLocation_$ID$(bpy.types.Panel):
    bl_label = "Select Panel Location"
    bl_idname = "SN_PT_SelectPanelLocation_$ID$"
    bl_space_type = '$SPACE$'
    bl_region_type = '$REGION$'
    bl_options = {"HIDE_HEADER"}
    $CATEGORY$

    def draw(self, context):
        
        if hasattr(context.space_data,"context"):
            row = self.layout.row()
            row.alert = True
            row.scale_y = 1.5
            op = row.operator("sn.select_panel",icon="EYEDROPPER",text="Any Context")
            op.space = context.space_data.type
            op.region = context.region.type
            op.context = ""
            op.category = ""
            op = row.operator("sn.select_panel",icon="EYEDROPPER",text=f"'{context.space_data.context.title()}' only")
            op.space = context.space_data.type
            op.region = context.region.type
            op.context = context.space_data.context.lower()
            op.category = ""
            
        else:
            row = self.layout.row()
            row.alert = True
            row.scale_y = 1.5
            op = row.operator("sn.select_panel",icon="EYEDROPPER",text="Select Location")
            op.space = context.space_data.type
            op.region = context.region.type
            op.context = ""
            op.category = "My Category"

bpy.utils.register_class(SN_PT_SelectPanelLocation_$ID$)
"""


remove_panels = []
panel_node = None


class SN_OT_StartPanelSelection(bpy.types.Operator):
    bl_idname = "sn.start_panel_selection"
    bl_label = "Select Panel"
    bl_description = "Start Panel Selection"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}
    
    node: bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        global remove_panels
        return len(remove_panels) == 0
    
    def get_panel_locations(self):
        regions = ["WINDOW", "HEADER", "CHANNELS", "TEMPORARY", "UI", "TOOLS", "TOOL_PROPS",
                "PREVIEW", "HUD", "NAVIGATION_BAR", "EXECUTE", "FOOTER", "TOOL_HEADER"]
        spaces = ["EMPTY", "VIEW_3D", "IMAGE_EDITOR", "NODE_EDITOR", "SEQUENCE_EDITOR", "CLIP_EDITOR",
                "DOPESHEET_EDITOR", "GRAPH_EDITOR", "NLA_EDITOR", "TEXT_EDITOR", "CONSOLE", "INFO",
                "TOPBAR", "STATUSBAR", "OUTLINER", "PROPERTIES", "FILE_BROWSER", "PREFERENCES"]
        locations = []
        for region in regions:
            for space in spaces:
                locations.append({"region":region,"space":space,"category":"Select Panel"})
        return locations

    def execute(self, context):
        global panel_node
        global panel_template
        global remove_panels
        panel_node = context.space_data.node_tree.nodes[self.node]
        locations = self.get_panel_locations()
        for index, location in enumerate(locations):
            panel = panel_template
            panel = panel.replace("$ID$",str(index))
            panel = panel.replace("$REGION$",location["region"])
            panel = panel.replace("$SPACE$",location["space"])
            panel = panel.replace("$CATEGORY$","bl_category=\""+location["category"]+"\"")
            try:
                exec(panel)
                remove_panels.append(f"bpy.utils.unregister_class(bpy.types.SN_PT_SelectPanelLocation_{str(index)})")
            except:
                pass
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}
    
    
def remove_registered_panels():
    global remove_panels
    for panel in remove_panels:
        try:
            exec(panel)
        except:
            pass
    remove_panels.clear()
    
    
class SN_OT_SelectPanel(bpy.types.Operator):
    bl_idname = "sn.select_panel"
    bl_label = "Select Location"
    bl_description = "Select this location for your panel"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}
    
    space: bpy.props.StringProperty(options={"SKIP_SAVE"})
    region: bpy.props.StringProperty(options={"SKIP_SAVE"})
    context: bpy.props.StringProperty(options={"SKIP_SAVE"})
    category: bpy.props.StringProperty(options={"SKIP_SAVE"})

    def execute(self, context):
        global panel_node
        if panel_node:
            panel_node.space = self.space
            panel_node.region = self.region
            panel_node.context = self.context
            panel_node.category = self.category
        panel_node = None
        remove_registered_panels()
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}




class SN_PanelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PanelNode"
    bl_label = "Panel"
    # bl_icon = "GRAPH"
    bl_width_default = 200
    
    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "has_collection": True
    }
    
    
    space: bpy.props.StringProperty(default="PROPERTIES")
    region: bpy.props.StringProperty(default="WINDOW")
    context: bpy.props.StringProperty()
    category: bpy.props.StringProperty(name="Category",
                                       description="The category this panel can be found in if required")
    
    
    hide_header: bpy.props.BoolProperty(default=False,
                                        name="Hide Header",
                                        description="Hides the header of this panel",
                                        update=SN_ScriptingBaseNode.auto_compile)
    
    
    default_closed: bpy.props.BoolProperty(default=False,
                                        name="Default Closed",
                                        description="Closes this panel by default",
                                        update=SN_ScriptingBaseNode.auto_compile)
    
    
    shortcut_only: bpy.props.BoolProperty(default=False,
                                          name="Shortcut Only",
                                          description="Only display this panel with a shortcut")
    
    
    label: bpy.props.StringProperty(default="New Panel",
                                    name="Label",
                                    description="The label of this panel",
                                    update=SN_ScriptingBaseNode.auto_compile)
    
    order: bpy.props.IntProperty(default=0,
                                 min=0,
                                 name="Order",
                                 description="This defines the order of the panels")
    

    def on_create(self,context):
        self.add_interface_output("Panel").removable = True
        self.add_dynamic_interface_output("Panel")
        self.add_dynamic_interface_output("Header")

        self.add_boolean_input("Poll")


    def draw_node(self,context,layout):
        if not self.shortcut_only:
            row = layout.row()
            row.scale_y = 1.5
            name = self.space.replace("_"," ").title() + " | " + self.region.replace("_"," ").title()
            row.operator("sn.start_panel_selection",text=name,icon="EYEDROPPER").node = self.name
            layout.prop(self, "category")
         
        layout.prop(self, "label")
        layout.prop(self, "hide_header")
        layout.prop(self, "default_closed")
        layout.prop(self, "shortcut_only")
        layout.prop(self, "order")
        
        
    def what_layout(self, socket):
        return "layout"
    
    
    def idname(self):
        return "SNA_PT_" + re.sub(r'\W+', '', self.label.replace(" ","_")) + "_" + self.uid
                

    def code_evaluate(self, context, touched_socket):
        
        option_closed = "\"DEFAULT_CLOSED\"," if self.default_closed else ""
        option_header = "\"HIDE_HEADER\"," if self.hide_header else ""
        
        space = self.space
        region = self.region
        context = self.context
        category = self.category
        
        if self.shortcut_only:
            space = "VIEW_3D"
            region = "WINDOW"
            context = ""
            category = ""
        
        return {
            "code": f"""
                    class {self.idname()}(bpy.types.Panel):
                        bl_label = "{self.label}"
                        bl_idname = "{self.idname()}"
                        bl_space_type = "{space}"
                        bl_region_type = "{region}"
                        {"bl_context = '"+context+"'" if context else ""}
                        {"bl_category = '"+category+"'" if category else ""}
                        {"bl_options = {"+option_closed+option_header+"}" if option_closed or option_header else ""}
                        bl_order = {self.order}
                        
                        @classmethod
                        def poll(cls, context):
                            return {self.inputs["Poll"].code()}

                        def draw_header(self, context):
                            try:
                                layout = self.layout
                                {self.outputs["Header"].by_name(8)}
                            except Exception as exc:
                                print(str(exc) + " | Error in {self.label} panel header")
                        
                        def draw(self, context):
                            try:
                                layout = self.layout
                                {self.outputs["Panel"].by_name(8)}
                            except Exception as exc:
                                print(str(exc) + " | Error in {self.label} panel")
                                
                    """
        }
        
    
    def code_register(self, context):     
        return {
            "code": f"""
                    bpy.utils.register_class({self.idname()})
                    
                    """
        }
        
    
    def code_unregister(self, context):
        return {
            "code": f"""
                    bpy.utils.unregister_class({self.idname()})
                    
                    """
        }