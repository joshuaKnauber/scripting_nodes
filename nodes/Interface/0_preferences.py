import bpy
import json
import os
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup
from ...node_tree.variables.variables_ui_list import SN_Variable
from ...interface.sidepanel.graph_panels import draw_property
from ...interface.menu.rightclick import construct_from_property
from ...compiler.compiler import create_addon_info, normalize_code


class SN_OT_GetSetPreferencesProperty(bpy.types.Operator):
    bl_idname = "sn.get_set_preferences_property"
    bl_label = "Get or Set Preferences Property"
    bl_description = "Get or set a property from your preferences"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def get_items(self, context):
        items = [("GETTER", "Getter", "Property getter"), ("INTERFACE", "Interface",
                                                           "Interface property"), ("SETTER", "Setter", "Property setter")]
        node = context.space_data.node_tree.nodes[self.node_name]
        if not node.properties[node.property_index].has_update():
            items.append(("UPDATE", "Update", "Update Function"))
        return items

    node_name: bpy.props.StringProperty()
    getset_type: bpy.props.EnumProperty(items=get_items,
                                        options={"SKIP_SAVE"},
                                        name="Getter/Setter",
                                        description="Add a getter/setter for your property")

    def add_node(self, tree):
        nodes = {"GETTER": "SN_GetPropertyNode",
                 "INTERFACE": "SN_DisplayPropertyNode",
                 "SETTER": "SN_SetPropertyNode",
                 "UPDATE": "SN_UpdatePropertyNode"}
        bpy.ops.node.add_node(
            "INVOKE_DEFAULT", type=nodes[self.getset_type], use_transform=True)
        if self.getset_type == "UPDATE":
            tree.nodes.active.wrong_add = False

    def execute(self, context):
        tree = context.space_data.node_tree
        node = tree.nodes[self.node_name]
        prop = node.properties[node.property_index]

        self.add_node(tree)
        
        idname = "__name__.partition('.')[0]"
        # if not node.addon_tree.doing_export:
        #     idname = node.addon_tree.sn_graphs[0].name
            
        tree.nodes.active.copied_path = construct_from_property(
            f"context.preferences.addons[{idname}].preferences", prop, node.uid)
        return {"FINISHED"}

    def draw(self, context):
        self.layout.prop(self, "getset_type", expand=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SN_AddonPreferencesNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AddonPreferencesNode"
    bl_label = "Addon Preferences"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.2, 0.2, 0.2),
        "starts_tree": True,
        "evaluate_once": True,
        "register_once": True,
        "unregister_once": True,
        "has_collection": True
    }

    properties: bpy.props.CollectionProperty(type=SN_Variable)
    property_index: bpy.props.IntProperty(name="Preferences Property Index")

    def on_create(self, context):
        self.add_interface_output("Preferences")
        self.add_dynamic_interface_output("Preferences")

    def on_free(self):
        for prop in self.properties:
            bpy.ops.sn.remove_node_property(node_name=self.name)

    def draw_node(self, context, layout):
        if len(self.collection.items) > 1:
            row = layout.row()
            row.alert = True
            row.label(text="You have multiple addon preferences", icon="ERROR")

        row = layout.row(align=False)
        row.template_list("SN_UL_VariableList", "Properties",
                          self, "properties", self, "property_index", rows=3)
        col = row.column(align=True)
        col.operator("sn.add_node_property", text="",
                     icon="ADD").node_name = self.name
        col = col.column(align=True)
        col.enabled = bool(len(self.properties))
        col.operator("sn.remove_node_property", text="",
                     icon="REMOVE").node_name = self.name
        col.operator("sn.edit_node_property", text="",
                     icon="GREASEPENCIL").node_name = self.name
        col.operator("sn.get_set_preferences_property", text="",
                     icon="FORWARD").node_name = self.name

    def remove_all_prefs(self):
        for addon in bpy.context.preferences.addons:
            if hasattr(addon.preferences, "is_sn_prefs_dev"):
                bpy.ops.preferences.addon_remove(module=addon.module)

    def code_evaluate(self, context, touched_socket):
        self.remove_all_prefs()

        property_register = []
        for prop in self.properties:
            property_register.append(prop.property_register())

        idname = "__name__.partition('.')[0]"
        if not self.addon_tree.doing_export:
            idname = f"'{self.addon_tree.sn_graphs[0].name}'"

        return {
            "code": f"""
                    class SNA_AddonPreferences_{self.uid}(bpy.types.AddonPreferences):
                        bl_idname = {idname}
                        
                        {'is_sn_prefs_dev: bpy.props.BoolProperty()' if not self.addon_tree.doing_export else ''}
                        {self.list_code(property_register, 6)}
                        
                        def draw(self, context):
                            try:
                                layout = self.layout
                                {self.outputs['Preferences'].by_name(8)}
                            except Exception as exc:
                                print(str(exc) + " | Error in addon preferences")
                    """
        }

    def write_placeholder_file(self, filepath):
        with open(filepath, "w") as placeholder:
            placeholder.seek(0)
            placeholder.write(normalize_code(
                create_addon_info(self.addon_tree), 0))
            placeholder.write("\n\ndef register(): pass")
            placeholder.write("\ndef unregister(): pass")
            placeholder.truncate()

    def code_register(self, context):
        filepath = os.path.join(os.path.dirname(
            __file__), "pref_addon", f"{self.addon_tree.sn_graphs[0].name}.py")
        self.write_placeholder_file(filepath)
        if self.addon_tree.doing_export:
            return {
                "code": f"""
                        bpy.utils.register_class(SNA_AddonPreferences_{self.uid})
                        """
            }
        else:
            return {
                "code": f"""
                        bpy.ops.preferences.addon_install(filepath=r"{filepath}")
                        bpy.ops.preferences.addon_enable(module="{self.addon_tree.sn_graphs[0].name}")
                        bpy.utils.register_class(SNA_AddonPreferences_{self.uid})
                        """
            }

    def code_unregister(self, context):
        if self.addon_tree.doing_export:
            return {
                "code": f"""
                        bpy.utils.unregister_class(SNA_AddonPreferences_{self.uid})
                        
                        """
            }
        else:
            return {
                "code": f"""
                        try: bpy.ops.preferences.addon_remove(module=r"{self.addon_tree.sn_graphs[0].name}")
                        except: pass
                        bpy.utils.unregister_class(SNA_AddonPreferences_{self.uid})
                        """
            }
