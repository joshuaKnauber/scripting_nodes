import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyNode import PropertyNode



class SN_PreferencesNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyNode):

    bl_idname = "SN_PreferencesNode"
    bl_label = "Preferences"
    bl_width_default = 200
    layout_type = "layout"
    is_trigger = True
    node_color = "INTERFACE"
    
    def on_create(self, context):
        self.add_boolean_input("Hide").default_value = False
        self.add_interface_output("Preferences")
        self.add_dynamic_interface_output("Preferences")

    def evaluate(self, context):
        props_imperative_list = self.props_imperative(context).split("\n")
        props_code_list = self.props_code(context).split("\n")
        props_register_list = self.props_register(context).split("\n")
        props_unregister_list = self.props_unregister(context).split("\n")
        
        idname = f"SNA_TempAddonPreferences_{self.static_uid}"
        prop_name = f"sna_addon_prefs_temp"

        self.code = f"""
                    {self.indent(props_imperative_list, 5)}
                    
                    class {idname}(bpy.types.PropertyGroup):
                        {self.indent(props_code_list, 6) if self.indent(props_code_list, 6).strip() else "pass"}

                    def sna_prefs(layout):
                        if not ({self.inputs["Hide"].python_value}):
                            self = bpy.context.scene.{prop_name}
                            {self.indent([out.python_value for out in self.outputs[:-1]], 7)}
                    """

        self.code_register = f"""
                            {self.indent(props_register_list, 7)}
                            bpy.utils.register_class({idname})
                            bpy.types.Scene.{prop_name} = bpy.props.PointerProperty(type={idname})
                            bpy.context.scene.sn.preferences.append(sna_prefs)
                            for a in bpy.context.screen.areas: a.tag_redraw()
                            """

        self.code_unregister = f"""
                            bpy.context.scene.sn.preferences.clear()
                            for a in bpy.context.screen.areas: a.tag_redraw()
                            del bpy.types.Scene.{prop_name}
                            bpy.utils.unregister_class({idname})
                            {self.indent(props_unregister_list, 7)}
                            """

    def evaluate_export(self, context):
        # TODO overwrite this for export
        self.evaluate(context)

    def draw_node(self, context, layout):
        layout.operator("sn.open_preferences", icon="PREFERENCES").navigation = "CUSTOM"
        amount = 0
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                amount += len(ntree.node_collection(self.bl_idname).refs)
        if amount > 1:
            layout.label(text="Multiple preferences nodes! Only one will be used", icon="ERROR")
            
        self.draw_list(layout)