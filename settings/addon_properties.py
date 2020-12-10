import bpy


class SN_AddonProperties(bpy.types.PropertyGroup):

    def get_addon_items(self,context):
        items = []
        for tree in bpy.data.node_groups:
            if tree.sn_addon_tree == tree:
                items.append((tree.name,tree.name,tree.name))
        return items

    editing_addon: bpy.props.EnumProperty(items=get_addon_items)