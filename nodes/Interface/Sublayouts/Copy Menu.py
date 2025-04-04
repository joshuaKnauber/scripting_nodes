import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_CopyMenuNodeNew(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_CopyMenuNodeNew"
    bl_label = "Copy Menu"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_interface_output().passthrough_layout_type = True
    
    menu_parent: bpy.props.StringProperty(name="Menu",
                                    default="VIEW3D_MT_add",
                                    description="The menu that should be displayed",
                                    update=SN_ScriptingBaseNode._evaluate)

    def evaluate(self, context):
        self.code = f"""
                    if hasattr(bpy.types,"{self.menu_parent}"):
                        if not hasattr(bpy.types.{self.menu_parent}, "poll") or bpy.types.{self.menu_parent}.poll(context):
                            bpy.types.{self.menu_parent}.draw(self, context)
                        else:
                            {self.active_layout}.label(text="Can't display this menu here!", icon="ERROR")
                    else:
                        {self.active_layout}.label(text="Can't display this menu!", icon="ERROR")
                    {self.indent(self.outputs[0].python_value, 5)}
                    """
                    
    def draw_node(self, context, layout):
        row = layout.row(align=True)
        name = f"{self.menu_parent.replace('_MT_', ' ').replace('_', ' ').title()}"
        op = row.operator("sn.activate_menu_picker", icon="EYEDROPPER", text=name)
        op.node_tree = self.node_tree.name
        op.node = self.name
        
    def draw_node_panel(self, context, layout):
        layout.prop(self, "menu_parent")