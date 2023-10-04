import bpy

from ...utils.is_serpens import in_sn_tree


class SN_PT_SettingsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_SettingsPanel"
    bl_label = "Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 3

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(heading="Debug")
        col.prop(sn, "show_node_code")


class SN_PT_DeveloperSettingsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_DeveloperSettingsPanel"
    bl_parent_id = "SN_PT_SettingsPanel"
    bl_label = "Developer Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw_node_refs(self, context: bpy.types.Context):
        sn = context.scene.sn
        self.layout.separator()
        layout = self.layout.column(align=True)
        for coll in sn.references.collections:
            box = layout.box()
            box.label(text=coll.name)
            col = box.column(align=True)
            col.enabled = False
            for node in coll.nodes:
                col.label(text="- " + node.name + " (" + node.id + ")")
            if len(coll.nodes) == 0:
                col.label(text="No nodes")
        if len(sn.references.collections) == 0:
            box = layout.box()
            box.label(text="No collections")

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(sn, "show_node_refs")
        if sn.show_node_refs:
            self.draw_node_refs(context)
