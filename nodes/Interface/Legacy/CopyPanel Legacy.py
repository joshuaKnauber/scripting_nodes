import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_CopyPanelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CopyPanelNode"
    bl_label = "Copy Panel (Legacy)"
    bl_width_default = 200
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()

    panel_parent: bpy.props.StringProperty(default="EEVEE_MATERIAL_PT_surface",
                                    name="Parent",
                                    description="The panel id this subpanel should be shown in",
                                    update=SN_ScriptingBaseNode._evaluate)
    
    def evaluate(self, context):
        self.code = f"""
                    if hasattr(bpy.types,"{self.panel_parent}"):
                        if not hasattr(bpy.types.{self.panel_parent}, "poll") or bpy.types.{self.panel_parent}.poll(context):
                            bpy.types.{self.panel_parent}.draw(self, context)
                        else:
                            {self.active_layout}.label(text="Can't display this panel here!", icon="ERROR")
                    else:
                        {self.active_layout}.label(text="Can't display this panel!", icon="ERROR")
                    """
                    
    def draw_node(self, context, layout):
        row = layout.row(align=True)
        op = row.operator("sn.activate_subpanel_picker", text=f"{self.panel_parent.replace('_PT_', ' ').replace('_', ' ').title()}", icon="EYEDROPPER")
        op.node_tree = self.node_tree.name
        op.node = self.name
        op.allow_subpanels = True        

    def draw_node_panel(self, context, layout):
        layout.prop(self, "panel_parent")