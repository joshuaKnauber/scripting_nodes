import bpy
from ..base_node import SN_ScriptingBaseNode



# extra evaluate to run something after evaluation is done
# keep track of changes to code -> only node code has changed; other code has changed
# if only node code has changed -> node_code_changed
# if also other code changed -> node_code_changed -> trigger roots



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
        uid = self.uuid
        self.code = f"""
                    class SNA_PT_HelloWorldPanel_{uid}(bpy.types.Panel):
                        bl_label = "Hello World Panel"
                        bl_idname = "SNA_PT_HelloWorldPanel_{uid}"
                        bl_space_type = 'PROPERTIES'
                        bl_region_type = 'WINDOW'
                        bl_context = "object"

                        def draw(self, context):
                            layout = self.layout
                            
                            {self.indent([out.python_value for out in self.outputs[:-1]], 7)}
                    """

        self.code_unregister = f"bpy.utils.unregister_class(SNA_PT_HelloWorldPanel_{uid})"
        self.code_register = f"bpy.utils.register_class(SNA_PT_HelloWorldPanel_{uid})"

    def draw_node(self, context, layout):
        pass