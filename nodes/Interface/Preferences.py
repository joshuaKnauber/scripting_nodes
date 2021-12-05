import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import get_python_name



class SN_PreferencesNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PreferencesNode"
    bl_label = "Preferences"
    bl_width_default = 200
    layout_type = "layout"
    is_trigger = True
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_output("Preferences")
        self.add_dynamic_interface_output("Preferences")

    def evaluate(self, context):
        self.code = f"""
                    def sna_prefs(layout):
                        pass
                        {self.indent([out.python_value for out in self.outputs[:-1]], 6)}
                    """

        self.code_register = f"""
                            bpy.context.scene.sn.preferences.append(sna_prefs)
                            for a in bpy.context.screen.areas: a.tag_redraw()
                            """
        self.code_unregister = f"""
                            bpy.context.scene.sn.preferences.clear()
                            for a in bpy.context.screen.areas: a.tag_redraw()
                            """

    def evalute_export(self, context):
        # TODO overwrite this for export
        self.evaluate(context)

    def draw_node(self, context, layout):
        pass