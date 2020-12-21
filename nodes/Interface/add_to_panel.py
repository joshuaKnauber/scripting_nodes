import bpy
import re
from ...node_tree.base_node import SN_ScriptingBaseNode


panel_locations = []


def sn_append_panel(self, context):
    row = self.layout.row()
    row.alert = True
    op = row.operator("sn.select_add_to_panel",text="Append Panel",icon="EYEDROPPER")
    op.panel = self.bl_idname
    op.append = True


def sn_prepend_panel(self, context):
    row = self.layout.row()
    row.alert = True
    op = row.operator("sn.select_add_to_panel",text="Prepend Panel",icon="EYEDROPPER")
    op.panel = self.bl_idname
    op.append = False


remove_panels = []
panel_node = None


class SN_OT_StartAddToPanelSelection(bpy.types.Operator):
    bl_idname = "sn.start_add_to_panel_selection"
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
            if hasattr(panel,"bl_space_type") and hasattr(panel,"bl_region_type"):
                panels.append(panel_name)
        return panels

    def execute(self, context):
        global panel_node
        global append_template
        global prepend_template
        global remove_panels
        panel_node = context.space_data.node_tree.nodes[self.node]
        for panel in self.get_panels():
            try:
                eval("bpy.types."+panel+".append(sn_append_panel)")
                eval("bpy.types."+panel+".prepend(sn_prepend_panel)")
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
            panel.remove(sn_prepend_panel)
        except:
            pass
    remove_panels.clear()
    
    
class SN_OT_SelectAddToPanel(bpy.types.Operator):
    bl_idname = "sn.select_add_to_panel"
    bl_label = "Select Location"
    bl_description = "Select this location for your panel"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}
    
    panel: bpy.props.StringProperty(options={"SKIP_SAVE"})
    append: bpy.props.BoolProperty(options={"SKIP_SAVE"})

    def execute(self, context):
        global panel_node
        panel_node.panel = self.panel
        panel_node.position = "APPEND" if self.append else "PREPEND"
        panel_node = None
        remove_registered_panels()
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}




class SN_AddToPanelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AddToPanelNode"
    bl_label = "Add To Panel"
    # bl_icon = "GRAPH"
    bl_width_default = 200
    
    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
    }
    
    
    panel: bpy.props.StringProperty(default="RENDER_PT_Context")
    
    
    position: bpy.props.EnumProperty(items=[("PREPEND","Prepend","Prepend"), ("APPEND","Append","Append")],
                                    name="Append/Prepend",
                                    description="Append or prepend the interface to the selected panel")
    

    def on_create(self,context):
        self.add_interface_output("Panel",True)
        self.add_dynamic_interface_output("Panel")


    def draw_node(self,context,layout):
        row = layout.row()
        row.scale_y = 1.5
        name = self.panel
        if "_" in name:
            name = name.replace("_PT_"," ").replace("_"," ").title()
        row.operator("sn.start_add_to_panel_selection",text=name,icon="EYEDROPPER").node = self.name
        layout.prop(self, "position", expand=True)
        
        
    def what_layout(self, socket):
        return "layout"
    
    
    def function_name(self):
        return f"sn_{'append' if self.position == 'APPEND' else 'prepend'}_panel_{self.uid}"
    

    def code_evaluate(self, context, touched_socket):

        panel_layouts = []
        for out in self.outputs:
            if out.name == "Panel":
                panel_layouts.append(out.block(0))
        
        return {
            "code": f"""
                    def {self.function_name()}(self,context):
                        layout = self.layout
                        {self.list_blocks(panel_layouts,6)}
                    """
        }
        
    
    def code_register(self, context):     
        return {
            "code": f"""
                    bpy.types.{self.panel}.{"append" if self.position == "APPEND" else "prepend"}({self.function_name()})
                    
                    """
        }
        
    
    def code_unregister(self, context):
        return {
            "code": f"""
                    bpy.types.{self.panel}.remove({self.function_name()})
                    
                    """
        }