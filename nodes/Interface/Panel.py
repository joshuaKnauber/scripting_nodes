import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_PanelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PanelNode"
    bl_label = "Panel"
    bl_width_default = 200
    layout_type = "layout"
    is_trigger = True
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_output()
        self.add_dynamic_interface_output()

    def evaluate(self, context):
        self.code = f"""
                    class SNA_PT_HelloWorldPanel(bpy.types.Panel):
                        bl_label = "Hello World Panel"
                        bl_idname = "OBJECT_PT_hello"
                        bl_space_type = 'PROPERTIES'
                        bl_region_type = 'WINDOW'
                        bl_context = "object"

                        def draw(self, context):
                            layout = self.layout

                            obj = context.object

                            row = layout.row()
                            row.label(text="Hello world!", icon='WORLD_DATA')

                            row = layout.row()
                            row.label(text="Active object is: " + obj.name)
                            row = layout.row()
                            row.prop(obj, "name")

                            row = layout.row()
                            row.operator("mesh.primitive_cube_add")
                    """

    def draw_node(self, context, layout):
        pass