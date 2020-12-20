import bpy
import re
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_OT_StartPanelSelection(bpy.types.Operator):
    bl_idname = "sn.start_panel_selection"
    bl_label = "Select Panel"
    bl_description = "Start Panel Selection"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        
        return {"FINISHED"}




class SN_PanelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PanelNode"
    bl_label = "Panel"
    # bl_icon = "GRAPH"
    bl_width_default = 200
    
    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "property_group": "sn_panel_nodes"
    }
    
    
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

        self.add_boolean_input("Poll")


    def draw_node(self,context,layout):        
        row = layout.row()
        row.scale_y = 1.5
        row.operator("sn.start_panel_selection",text="Outer Rim",icon="EYEDROPPER")
         
        layout.prop(self, "label")
        layout.prop(self, "hide_header")
        layout.prop(self, "default_closed")
        
        
    def what_layout(self, socket):
        return "layout"
    
    
    def idname(self):
        return "SNA_PT_" + re.sub(r'\W+', '', self.label.replace(" ","_")) + "_" + self.uid
                

    def code_evaluate(self, context, touched_socket):
        
        label = self.label
        
        space_type = "PROPERTIES"
        region_type = "WINDOW"
        context = "object"
        category = ""
        
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
                        bl_label = "{label}"
                        bl_idname = "{self.idname()}"
                        bl_space_type = "{space_type}"
                        bl_region_type = "{region_type}"
                        {"bl_context = '"+context+"'" if context else ""}
                        {"bl_category = '"+category+"'" if category else ""}
                        {"bl_options = {"+option_closed+option_header+"}" if option_closed or option_header else ""}
                        bl_order = {0}
                        
                        @classmethod
                        def poll(cls, context):
                            return {self.inputs["Poll"].value}

                        def draw_header(self, context):
                            layout = self.layout
                            {self.list_blocks(header_layouts, 7)}
                        
                        def draw(self, context):
                            layout = self.layout
                            {self.list_blocks(panel_layouts, 7)}
                            
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