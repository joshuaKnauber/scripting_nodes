import bpy
from ...packages import package_ops



class SN_PT_PackagesPanel(bpy.types.Panel):
    bl_idname = "SN_PT_PackagesPanel"
    bl_label = ""
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 6
    bl_options = {"DEFAULT_CLOSED", "HEADER_LAYOUT_EXPAND"}

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Packages")
        layout.operator("wm.url_open", text="", icon="QUESTION", emboss=False).url = "https://joshuaknauber.notion.site/Packages-Snippets-5fc9492b640146a2bcafb269d4a9e876"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.2
        row.operator("sn.open_preferences", text="Get Packages", icon="URL").navigation = "MARKET"
        layout.separator()

        row = layout.row(align=True)
        row.operator("sn.install_package", text="Install Package", icon="FILE_FOLDER")
        row.operator("sn.reload_packages", text="", icon="FILE_REFRESH")

        if package_ops.require_reload:
            row = layout.row()
            row.alert = True
            row.label(text="Restart blender to see package!", icon="INFO")

        for i, package in enumerate(package_ops.loaded_packages):
            box = layout.box()
            col = box.column(align=True)
            row = col.row()
            row.label(text=package["name"])
            if package["wiki"]:
                row.operator("wm.url_open", text="", icon="URL", emboss=False).url = package["wiki"]
            row.operator("sn.uninstall_package", text="", icon="PANEL_CLOSE", emboss=False).index = i

            if package["description"]:
                row = col.row()
                row.enabled = False
                row.label(text=package["description"])
            if package["author"]:
                row = col.row()
                row.enabled = False
                row.label(text="By: "+package["author"])
            if package["version"]:
                row = col.row()
                row.enabled = False
                row.label(text=package["version"])

        if not package_ops.loaded_packages:
            box = layout.box()
            box.label(text="No packages installed!", icon="INFO")