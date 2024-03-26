import bpy
from ...core.bd_browser import search, scraper


class SNA_PT_navigation_bar(bpy.types.Panel):
    bl_label = "Preferences Navigation"
    bl_space_type = "PREFERENCES"
    bl_region_type = "NAVIGATION_BAR"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        return context.scene.sna.show_bd_browser

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sna = context.scene.sna


class SNA_PT_FilterDataSettings(bpy.types.Panel):
    bl_idname = "SNA_PT_FilterDataSettings"
    bl_label = "Filter"
    bl_space_type = "PREFERENCES"
    bl_region_type = "WINDOW"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        return context.scene.sna.show_bd_browser

    def draw(self, context: bpy.types.Context):
        layout = self.layout


class SNA_PT_data_search(bpy.types.Panel):
    bl_space_type = "PREFERENCES"
    bl_region_type = "WINDOW"
    bl_label = "Display"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        return context.scene.sna.show_bd_browser

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sna = context.scene.sna

        layout.operator("sna.scrape")

        if scraper.BLENDER_DATA.keys():
            layout.prop(sna, "blend_data_search", icon="VIEWZOOM", text="")
            layout.prop(sna, "blend_data_filter")
            layout.prop(sna, "blend_data_groupby")

            for i, group in enumerate(search.SEARCH_RESULTS.keys()):
                if i >= 10:
                    layout.label(text=f"{len(search.SEARCH_RESULTS) - i} more...")
                    break

                layout.label(text=f"{sna.blend_data_groupby}: {group}")
                col = layout.column(align=True)

                for j, result in enumerate(search.SEARCH_RESULTS[group]):
                    if j >= 10:
                        col.label(
                            text=f"{len(search.SEARCH_RESULTS[group]) - i} more..."
                        )
                        break
                    item = scraper.BLENDER_DATA[result["key"]]

                    box = col.box()
                    boxcol = box.column(align=True)
                    boxcol.label(text=f"{item['name']}")
                    if item["description"]:
                        row = boxcol.row()
                        row.enabled = False
                        row.label(text=item["description"])
                    row = boxcol.row()
                    row.enabled = False
                    row.label(text=", ".join(item["paths"]))
