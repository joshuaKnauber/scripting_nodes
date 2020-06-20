import bpy

class UiLocationHandler():

    region_cache = {}
    space_region_cache = {}
    context_cache = {}

    def _list_to_items(self,list_items):
        """ returns the list of string as items """
        items = []
        for item in list_items:
            items.append( (item,item.replace("_"," ").title(),item.replace("_"," ").title()) )
        return items

    def space_type_items(self):
        """ returns the space type items """
        types = ["VIEW_3D", "IMAGE_EDITOR", "NODE_EDITOR", "SEQUENCE_EDITOR", "CLIP_EDITOR",
                "DOPESHEET_EDITOR", "GRAPH_EDITOR", "NLA_EDITOR", "TEXT_EDITOR", "CONSOLE",
                "INFO", "TOPBAR", "STATUSBAR", "OUTLINER", "PROPERTIES", "FILE_BROWSER", "PREFERENCES"]
        return self._list_to_items(types)

    def _get_region_types_from_space(self, space_type):
        """ returns the possible region types for the given space type """
        types = []
        for panel in dir(bpy.types):
            if "_PT_" in panel:
                panel = eval("bpy.types." + panel)
                if panel.bl_space_type == space_type:
                    if not panel.bl_region_type in types:
                        types.append(panel.bl_region_type)
        return types

    def region_type_items(self, space_type):
        """ returns the region type items """
        if space_type in self.region_cache:
            return self.region_cache[space_type]
        else:
            types = self._get_region_types_from_space(space_type)
            items = self._list_to_items(types)
            self.region_cache[space_type] = items
            return items

    def region_type_names(self, space_type):
        """ return a list of the names of the region types for the space type """
        items = []
        for name in self.region_type_items(space_type):
            items.append(name[0])
        return items

    def space_region_has_categories(self, space_type, region_type):
        """ returns if the given space region has categories """
        if space_type + "-" + region_type in self.space_region_cache:
            return self.space_region_cache[space_type + "-" + region_type]
        else:
            for panel in dir(bpy.types):
                if "_PT_" in panel:
                    panel = eval("bpy.types." + panel)
                    if panel.bl_space_type == space_type and panel.bl_region_type == region_type:
                        try:
                            panel.bl_category
                            self.space_region_cache[space_type + "-" + region_type] = True
                            return True
                        except AttributeError:
                            pass
            self.space_region_cache[space_type + "-" + region_type] = False
            return False

    def context_items(self, space_type, region_type):
        """ returns the contexts of the given space region """
        if space_type + "-" + region_type in self.context_cache:
            return self.context_cache[space_type + "-" + region_type]
        else:
            contexts = []
            for panel in dir(bpy.types):
                if "_PT_" in panel:
                    panel = eval("bpy.types." + panel)
                    if panel.bl_space_type == space_type and panel.bl_region_type == region_type:
                        try:
                            if not panel.bl_context[:1] == ".":
                                if not panel.bl_context in contexts:
                                    contexts.append( panel.bl_context )
                        except AttributeError:
                            pass
            items = self._list_to_items(contexts)
            self.context_cache[space_type + "-" + region_type] = items
            return items

    def _get_unique_panel_name(self, panel_name, panels):
        """ looks for panels with the same name and adds a unique number if necessarry """
        existing = 0
        for panel in panels:
            if ("-").join(panel[0].split("-")[:-1]).rstrip() == panel_name or panel[0] == panel_name:
                existing += 1
        if existing:
            panel_name += " - " + str(existing)
        return panel_name

    def get_panels(self, space_type, region_type):
        """ returns all panels for the space region """
        panels = []
        for panel in dir(bpy.types):
            if "_PT_" in panel:
                idname = panel
                panel = eval("bpy.types."+panel)
                if panel.bl_space_type == space_type:
                    if panel.bl_region_type == region_type:
                        panel_name = panel.bl_label
                        if panel_name:
                            try:
                                panel_name += " - " + panel.bl_context.title()
                            except:
                                pass
                            try:
                                panel_name += " - " + panel.bl_category
                            except:
                                pass
                            panel_name = self._get_unique_panel_name(panel_name,panels)
                            panels.append((panel_name,idname))

        return panels