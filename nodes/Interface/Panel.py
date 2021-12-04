import bpy
from ..base_node import SN_ScriptingBaseNode



def register_dummy_panel(space, region):
    panel = f"""
class SN_PT_Dummy{space}{region}(bpy.types.Panel):
    bl_label = "test"
    bl_space_type = '{space}'
    bl_region_type = '{region}'
    bl_context = "object"
    bl_category = "SELECT"

    bl_options = {{"HIDE_HEADER"}}
    bl_order = 0
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.5
        row.alert = True
        row.operator("sn.select_panel_location", text="Select {space} {region}")
    
bpy.utils.register_class(SN_PT_Dummy{space}{region})
"""
    exec(panel)
     



class SN_OT_SelectPanelLocation(bpy.types.Operator):
    bl_idname = "sn.select_panel_location"
    bl_label = "Select Panel Location"
    bl_description = "Select the location of this panel in the Interface"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        space_types = ["EMPTY", "VIEW_3D", "IMAGE_EDITOR", "NODE_EDITOR",
                        "SEQUENCE_EDITOR", "CLIP_EDITOR", "DOPESHEET_EDITOR",
                        "GRAPH_EDITOR", "NLA_EDITOR", "TEXT_EDITOR", "CONSOLE",
                        "INFO", "TOPBAR", "STATUSBAR", "OUTLINER", "PROPERTIES",
                        "FILE_BROWSER", "SPREADSHEET", "PREFERENCES"]
        region_types = ["WINDOW", "HEADER", "CHANNELS", "TEMPORARY", "UI", "TOOLS",
                        "TOOL_PROPS", "PREVIEW", "HUD", "NAVIGATION_BAR", "EXECUTE",
                        "FOOTER", "TOOL_HEADER", "XR"]
        
        for region in region_types:
            for space in space_types:
                try:
                    register_dummy_panel(space, region)
                except Exception as error:
                    print(error)
        
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}




class SN_PanelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PanelNode"
    bl_label = "Panel"
    bl_width_default = 200
    layout_type = "layout"
    is_trigger = True
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_boolean_input("Hide")
        self.add_interface_output("Panel")
        self.add_dynamic_interface_output("Panel")
        self.add_interface_output("Header")
        self.add_dynamic_interface_output("Header")

    label: bpy.props.StringProperty(default="New Panel",
                                    name="Label",
                                    description="The label of your panel",
                                    update=SN_ScriptingBaseNode._evaluate)

    def evaluate(self, context):
        uid = self.uuid
        # TODO make a function to get a valid python representation of a string for var names
        idname = f"SNA_PT_{self.label.title().replace(' ', '') if self.label else 'Panel'}_{uid}"
        self.code = f"""
                    class {idname}(bpy.types.Panel):
                        bl_label = "{self.label}"
                        bl_idname = "{idname}"
                        bl_space_type = 'PROPERTIES'
                        bl_region_type = 'WINDOW'
                        bl_context = "object"

                        @classmethod
                        def poll(cls, context):
                            return not {self.inputs["Hide"].python_value}
                        
                        def draw_header(self, context):
                            layout = self.layout
                            {self.indent([out.python_value for out in filter(lambda out: out.name=='Header' and not out.dynamic, self.outputs)], 7)}

                        def draw(self, context):
                            layout = self.layout
                            {self.indent([out.python_value for out in filter(lambda out: out.name=='Panel' and not out.dynamic, self.outputs)], 7)}
                    """

        self.code_unregister = f"bpy.utils.unregister_class({idname})"
        self.code_register = f"bpy.utils.register_class({idname})"

    def draw_node(self, context, layout):
        row = layout.row()
        row.scale_y = 1.5
        row.operator("sn.select_panel_location")
        layout.prop(self, "label")