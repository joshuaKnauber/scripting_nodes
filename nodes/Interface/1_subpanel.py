import bpy
import re
from ...node_tree.base_node import SN_ScriptingBaseNode


panel_locations = []


def sn_append_panel(self, context):
    
    if hasattr(context.space_data,"context"):
        row = self.layout.row()
        row.alert = True
        row.scale_y = 1.5
        op = row.operator("sn.select_subpanel",text="Select Panel",icon="EYEDROPPER")
        op.panel = self.bl_idname
        op.space = context.space_data.type
        op.region = context.region.type
        op.context = context.space_data.context.lower()
    else:
        row = self.layout.row()
        row.alert = True
        row.scale_y = 1.5
        op = row.operator("sn.select_subpanel",text="Select Panel",icon="EYEDROPPER")
        op.panel = self.bl_idname
        op.space = context.space_data.type
        op.region = context.region.type
        op.context = ""


remove_panels = []
panel_node = None


class SN_OT_StartSubPanelSelection(bpy.types.Operator):
    bl_idname = "sn.start_subpanel_selection"
    bl_label = "Select Panel"
    bl_description = "Start Panel Selection"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}
    
    node: bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        global remove_panels
        return len(remove_panels) == 0
    
    def get_panels(self):
        panels = []
        for panel_name in dir(bpy.types):
            panel = eval("bpy.types."+panel_name)
            if hasattr(panel,"bl_space_type") and hasattr(panel,"bl_region_type") and not hasattr(panel,"bl_parent_id"):
                panels.append(panel_name)
        return panels

    def execute(self, context):
        global panel_node
        global append_template
        global remove_panels
        panel_node = context.space_data.node_tree.nodes[self.node]
        for panel in self.get_panels():
            try:
                eval("bpy.types."+panel+".append(sn_append_panel)")
                remove_panels.append(eval("bpy.types."+panel))
            except:
                pass
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}
    
    
def remove_registered_panels():
    global remove_panels
    for panel in remove_panels:
        try:
            panel.remove(sn_append_panel)
        except:
            pass
    remove_panels.clear()
    
    
class SN_OT_SelectSubPanel(bpy.types.Operator):
    bl_idname = "sn.select_subpanel"
    bl_label = "Select Location"
    bl_description = "Select this location for your subpanel"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}
    
    panel: bpy.props.StringProperty(options={"SKIP_SAVE"})
    space: bpy.props.StringProperty(options={"SKIP_SAVE"})
    region: bpy.props.StringProperty(options={"SKIP_SAVE"})
    context: bpy.props.StringProperty(options={"SKIP_SAVE"})

    def execute(self, context):
        global panel_node
        if panel_node:
            panel_node.panel = self.panel
            panel_node.space = self.space
            panel_node.region = self.region
            panel_node.context = self.context
        panel_node = None
        remove_registered_panels()
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}




class SN_SubpanelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SubpanelNode"
    bl_label = "Sub Panel"
    # bl_icon = "GRAPH"
    bl_width_default = 200
    
    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "register_order": 1
    }
    
    
    space: bpy.props.StringProperty(default="PROPERTIES")
    region: bpy.props.StringProperty(default="WINDOW")
    context: bpy.props.StringProperty(default="render")
    
    panel: bpy.props.StringProperty(default="RENDER_PT_context")
    
    
    hide_header: bpy.props.BoolProperty(default=False,
                                        name="Hide Header",
                                        description="Hides the header of this panel",
                                        update=SN_ScriptingBaseNode.update_needs_compile)
    
    
    default_closed: bpy.props.BoolProperty(default=False,
                                        name="Default Closed",
                                        description="Closes this panel by default",
                                        update=SN_ScriptingBaseNode.update_needs_compile)
    
    
    label: bpy.props.StringProperty(default="New Panel",
                                    name="Label",
                                    description="The label of this panel",
                                    update=SN_ScriptingBaseNode.update_needs_compile)
    

    def on_create(self,context):
        self.add_interface_output("Panel",True)
        self.add_dynamic_interface_output("Panel")
        self.add_dynamic_interface_output("Header")

        self.add_boolean_input("Poll").set_default(True)


    def draw_node(self,context,layout):
        row = layout.row()
        row.scale_y = 1.5
        name = self.panel
        if "_" in name:
            name = name.replace("_PT_"," ").replace("_"," ").title()
        row.operator("sn.start_subpanel_selection",text=name,icon="EYEDROPPER").node = self.name
         
        layout.prop(self, "label")
        layout.prop(self, "hide_header")
        layout.prop(self, "default_closed")
        
        
    def what_layout(self, socket):
        return "layout"
    
    
    def idname(self):
        return "SNA_PT_" + re.sub(r'\W+', '', self.label.replace(" ","_")) + "_" + self.uid
                

    def code_evaluate(self, context, touched_socket):
        
        option_closed = "\"DEFAULT_CLOSED\"," if self.default_closed else ""
        option_header = "\"HIDE_HEADER\"," if self.hide_header else ""
        
        panel_layouts = []
        for out in self.outputs:
            if out.name == "Panel":
                panel_layouts.append(out.block(0))
        
        header_layouts = []
        for out in self.outputs:
            if out.name == "Header":
                header_layouts.append(out.block(0))
        
        return {
            "code": f"""
                    class {self.idname()}(bpy.types.Panel):
                        bl_label = "{self.label}"
                        bl_idname = "{self.idname()}"
                        bl_parent_id = "{self.panel}"
                        bl_space_type = "{self.space}"
                        bl_region_type = "{self.region}"
                        {"bl_context = '"+self.context+"'" if self.context else ""}
                        {"bl_options = {"+option_closed+option_header+"}" if option_closed or option_header else ""}
                        
                        @classmethod
                        def poll(cls, context):
                            return {self.inputs["Poll"].value}

                        def draw_header(self, context):
                            try:
                                layout = self.layout
                                {self.list_blocks(header_layouts, 8)}
                            except Exception as exc:
                                print(str(exc) + " | Error in {self.label} subpanel header")
                        
                        def draw(self, context):
                            try:
                                layout = self.layout
                                {self.list_blocks(panel_layouts, 8)}
                            except Exception as exc:
                                print(str(exc) + " | Error in {self.label} subpanel")
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