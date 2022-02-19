def get_sorted_props(prop_list):
    """ Returns a list of the properties, sorted for registering """
    # sort groups to the top of the list
    prop_list.sort(key=lambda prop: prop.property_type == "Group", reverse=True)
    # split property groups with collections or pointers with use prop group enabled
    prop_groups = list(filter(lambda prop: prop.property_type == "Group", prop_list))
    other_props = list(filter(lambda prop: not prop in prop_groups, prop_list))
    ref_prop_groups = list(filter(_is_propgroup_with_references, prop_groups))
    prop_groups = list(filter(lambda prop: not prop in ref_prop_groups, prop_groups))
    # TODO sort ref_prop_groups -> may fail if a prop group has a prop with a collection or pointer to another prop group with the same
    return prop_groups + ref_prop_groups + other_props


def _is_propgroup_with_references(prop):
    """ Returns if the given property group has pointer or collection props with references to other prop groups """
    for subprop in prop.settings.properties:
        if subprop.property_type == "Collection" and subprop.settings.prop_group in prop.prop_collection_origin.properties:
            return True
        elif subprop.property_type == "Pointer" and subprop.settings.use_prop_group and subprop.settings.prop_group in prop.prop_collection_origin.properties:
            return True
    return False