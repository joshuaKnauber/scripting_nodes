import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_AddToPanelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AddToPanelNode"
    bl_label = "Add To Panel (Legacy)"
    bl_width_default = 200
    def layout_type(self, _): return "layout"
    is_trigger = True
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_boolean_input("Hide")
        self.add_interface_output("Panel").prev_dynamic = True
        self.add_dynamic_interface_output("Panel")


    append: bpy.props.EnumProperty(default="APPEND", items=[
                                    ("PREPEND", "Prepend", "Prepend this to the start of the panel"),
                                    ("APPEND", "Append", "Append this to the end of the panel")],
                                    name="Position",
                                    description="Position of this interface to the selected panel",
                                    update=SN_ScriptingBaseNode._evaluate)

    panel_parent: bpy.props.StringProperty(default="EEVEE_MATERIAL_PT_surface",
                                    name="Parent",
                                    description="The panel id this subpanel should be shown in",
                                    update=SN_ScriptingBaseNode._evaluate)


    def evaluate(self, context):
        uid = self.uuid
        func_name = f"sna_add_to_{self.panel_parent.lower()}_{uid}"

        self.code = f"""
                    def {func_name}(self, context):
                        if not ({self.inputs["Hide"].python_value}):
                            layout = self.layout
                            {self.indent([out.python_value for out in self.outputs[:-1]], 7)}
                    """

        self.code_register = f"bpy.types.{self.panel_parent}.{self.append.lower()}({func_name})"
        self.code_unregister = f"bpy.types.{self.panel_parent}.remove({func_name})"


    def draw_node(self, context, layout):
        row = layout.row()
        row.scale_y = 1.3
        op = row.operator("sn.activate_subpanel_picker", text=f"{self.panel_parent.replace('_PT_', ' ').replace('_', ' ').title()}", icon="EYEDROPPER")
        op.node_tree = self.node_tree.name
        op.node = self.name
        op.allow_subpanels = True
        
        layout.prop(self, "append", expand=True)


    def draw_node_panel(self, context, layout):
        layout.prop(self, "panel_parent")