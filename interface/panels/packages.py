import bpy
from ...packages import package_ops
from ...packages import snippet_ops



class SN_PT_ExtensionsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_ExtensionsPanel"
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
        layout.label(text="Extensions")
        layout.operator("wm.url_open", text="", icon="QUESTION", emboss=False).url = "https://joshuaknauber.notion.site/Packages-Snippets-5fc9492b640146a2bcafb269d4a9e876"

    def draw(self, context):
        layout = self.layout
            
            
            
class SN_PT_SnippetsPanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_ExtensionsPanel"
    bl_idname = "SN_PT_SnippetsPanel"
    bl_label = ""
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"HEADER_LAYOUT_EXPAND"}
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Snippets")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.1
        row.operator("sn.open_preferences", text="Get Snippets", icon="URL").navigation = "MARKET"

        node = context.space_data.node_tree.nodes.active
        row = layout.row()
        row.scale_y = 1.1
        if node and node.select and node.bl_idname in ["SN_RunFunctionNode", "SN_RunInterfaceFunctionNode"]:
            if getattr(node, "ref_SN_FunctionNode", None) or getattr(node, "ref_SN_InterfaceFunctionNode", None):
                op = row.operator("sn.export_snippet", text="Export Snippet", icon="EXPORT", depress=True)
                op.node = node.name
                op.tree = node.node_tree.name
            else:
                box = row.box()
                box.label(text="Select a valid Run Function node to export a snippet", icon="EXPORT")
        else:
            box = row.box()
            box.label(text="Select Run Function node to export a snippet", icon="EXPORT")
        layout.separator()

        row = layout.row()
        row.scale_y = 1.1
        row.operator("sn.install_snippet", text="Install Snippets", icon="FILE_FOLDER")
        
        for i, snippet in enumerate(snippet_ops.loaded_snippets):
            box = layout.box()
            row = box.row()
            if type(snippet) == str:
                row.label(text=snippet.split(".")[0])
                row.operator("sn.uninstall_snippet", text="", icon="PANEL_CLOSE", emboss=False).index = i
            else:
                row.label(text=snippet["name"])
                row.operator("sn.uninstall_snippet", text="", icon="PANEL_CLOSE", emboss=False).index = i
                row = box.row()
                split = row.split(factor=0.1)
                split.label(text="")
                col = split.column(align=True)
                col.enabled = False
                for name in snippet["snippets"]:
                    col.label(text=name.split(".")[0])
                
        if not snippet_ops.loaded_snippets:
            box = layout.box()
            box.label(text="No snippets installed!", icon="INFO")

        
            
class SN_PT_PackagesPanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_ExtensionsPanel"
    bl_idname = "SN_PT_PackagesPanel"
    bl_label = ""
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED", "HEADER_LAYOUT_EXPAND"}
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Packages")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.1
        row.operator("sn.open_preferences", text="Get Packages", icon="URL").navigation = "MARKET"
        layout.separator()

        row = layout.row(align=True)
        row.scale_y = 1.1
        row.operator("sn.install_package", text="Install Package", icon="FILE_FOLDER")
        row.operator("sn.reload_packages", text="", icon="FILE_REFRESH")

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

        if package_ops.require_reload:
            row = layout.row()
            row.alert = True
            row.label(text="Restart blender to see package!", icon="INFO")