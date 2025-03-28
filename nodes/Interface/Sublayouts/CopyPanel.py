import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_CopyPanelNodeNew(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_CopyPanelNodeNew"
    bl_label = "Copy Panel"
    bl_width_default = 200
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_interface_output().passthrough_layout_type = True

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
                    {self.indent(self.outputs[0].python_value, 5)}
                    """
                    
    def draw_node(self, context, layout):
        row = layout.row(align=True)
        op = row.operator("sn.activate_subpanel_picker", text=f"{self.panel_parent.replace('_PT_', ' ').replace('_', ' ').title()}", icon="EYEDROPPER")
        op.node_tree = self.node_tree.name
        op.node = self.name
        op.allow_subpanels = True        

    def draw_node_panel(self, context, layout):
        layout.prop(self, "panel_parent")