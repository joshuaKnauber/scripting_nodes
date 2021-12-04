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
        layout.prop(self, "label")