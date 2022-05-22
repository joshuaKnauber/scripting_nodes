import bpy



class SN_MT_PresetMenu(bpy.types.Menu):
    bl_idname = "SN_MT_PresetMenu"
    bl_label = "Presets"

    def draw(self, context):
        layout = self.layout
        prefs = bpy.context.preferences.addons[__name__.partition('.')[ 0]].preferences
        
        for i, preset in enumerate(prefs.presets):
            layout.operator("sn.load_preset", text=preset.name).index = i

        if not len(prefs.presets):
            layout.label(text="No presets", icon="INFO")
        
        layout.separator()

        node = context.space_data.node_tree.nodes.active
        if node:
            layout.operator("sn.add_preset", icon="ADD", text=f"Add '{node.label if node.label else node.name}'")
        else:
            layout.operator("sn.add_preset", icon="ADD")

        row = layout.row()
        row.enabled = len(prefs.presets) > 0
        row.operator("sn.remove_presets", text="Remove Preset", icon="REMOVE")
            


def preset_menu(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.bl_idname == "ScriptingNodesTree":
        layout = self.layout
        layout.menu("SN_MT_PresetMenu", text="Presets")