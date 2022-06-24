import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_PieMenuNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PieMenuNode"
    bl_label = "Pie Menu"
    def layout_type(self, _): return "layout"
    is_trigger = True
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_boolean_input("Hide")
        self.add_interface_output("Menu")

    idname_override: bpy.props.StringProperty(default="",
                                name="Idname Override",
                                description="Use this if you want to define the idname of this panel yourself",
                                update=SN_ScriptingBaseNode._evaluate)

    title: bpy.props.StringProperty(default="",
                                name="Label",
                                description="The label shown at the top of this menu",
                                update=SN_ScriptingBaseNode._evaluate)

    @property
    def idname(self):
        if self.idname_override:
            return self.idname_override
        return f"SNA_MT_{self.static_uid}"

    def evaluate(self, context):
        self.trigger_ref_update()
        self.code = f"""
            class {self.idname}(bpy.types.Menu):
                bl_idname = "{self.idname}"
                bl_label = "{self.title}"

                @classmethod
                def poll(cls, context):
                    return not ({self.inputs["Hide"].python_value})

                def draw(self, context):
                    layout = self.layout.menu_pie()
                    {self.indent([out.python_value for out in self.outputs], 5)}
            """
        
        self.code_register = f"""
            bpy.utils.register_class({self.idname})
            """
        
        self.code_unregister = f"""
            bpy.utils.unregister_class({self.idname})
            """

    def draw_node(self, context, layout):
        layout.prop(self, "name")
        layout.prop(self, "title")
    
    def draw_node_panel(self, context, layout):
        layout.prop(self, "idname_override")