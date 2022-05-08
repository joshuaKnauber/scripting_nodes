import bpy


def get_filtered_properties():
    filtered = []
    sn = bpy.context.scene.sn
    for prop in sn.properties:
        cat_list = list(map(lambda cat: cat.name, sn.property_categories))
        if sn.active_prop_category == "ALL":
            filtered.append(prop)
        elif sn.active_prop_category == "OTHER":
            if prop.category == "OTHER" or not prop.category or not prop.category in cat_list:
                filtered.append(prop)
        elif prop.category == sn.active_prop_category:
            filtered.append(prop)
    return filtered

def get_selected_property():
    sn = bpy.context.scene.sn
    if sn.property_index < len(sn.properties):
        prop = sn.properties[sn.property_index]
        cat_list = list(map(lambda cat: cat.name, sn.property_categories))

        if sn.active_prop_category == "ALL":
            return prop
        elif sn.active_prop_category == "OTHER":
            if prop.category == "OTHER" or not prop.category or not prop.category in cat_list:
                return prop
        elif prop.category == sn.active_prop_category:
            return prop
    return None

def get_selected_property_offset(offset):
    selected = get_selected_property()
    filtered = get_filtered_properties()
    if selected:
        i = filtered.index(selected)
        i += offset
        if i >= 0 and i < len(filtered):
            return filtered[i]
    return None


class SN_UL_PropertyList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text="", icon=item.icon)
        row.prop(item, "name", emboss=False, text="")
        if not item.property_type == "Group":
            row.operator("sn.copy_python_name", text="", icon="COPYDOWN", emboss=False).name = item.data_path
        if context.scene.sn.show_property_categories:
            row.operator("sn.move_property_category", text="", icon="FORWARD", emboss=False).index = index

    def filter_items(self, context, data, propname):
        sn = context.scene.sn
        
        if sn.active_prop_category == "ALL":
            return [], []
        
        elif sn.active_prop_category == "OTHER":
            flt_flags = []
            cat_list = list(map(lambda cat: cat.name, sn.property_categories))
            for prop in sn.properties:
                if prop.category == "OTHER" or not prop.category or not prop.category in cat_list:
                    flt_flags.append(self.bitflag_filter_item)
                else:
                    flt_flags.append(0)
            return flt_flags, []
        
        else:
            flt_flags = []
            for prop in sn.properties:
                if prop.category == sn.active_prop_category:
                    flt_flags.append(self.bitflag_filter_item)
                else:
                    flt_flags.append(0)
            return flt_flags, []