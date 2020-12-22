import bpy
import re


def name_is_unique(collection, name):
    count = 0
    for item in collection:
        if item.name == name:
            count += 1
    return count <= 1

def get_unique_name(collection, base_name):
    if name_is_unique(collection, base_name):
        return base_name
    else:
        max_num = 0
        if "_" in base_name and base_name.split("_")[-1].isnumeric():
            base_name = ("_").join(base_name.split("_")[:-1])
        for item in collection:
            if "_" in item.name and item.name.split("_")[-1].isnumeric():
                item_base_name = ("_").join(item.name.split("_")[:-1])
                if item_base_name == base_name:
                    max_num = max(max_num, int(item.name.split("_")[-1]))
        return base_name + "_" + str(max_num+1).zfill(3)



class SN_Icon(bpy.types.PropertyGroup):

    def update_name(self,context):
        # update icon nodes
        if self.old_name:
            for graph in context.scene.sn.addon_tree().sn_graphs:
                for node in graph.node_tree.nodes:
                    if node.bl_idname == "SN_GetIconNode":
                        if node.custom_icon == self.old_name:
                            node.custom_icon = self.name
        self.old_name = self.name

        # correct name
        proper_name = re.sub(r'\W+', '', self.name.replace(" ","_").upper())
        if not proper_name:
            proper_name = "ICON"
        proper_name = get_unique_name(context.scene.sn.addon_tree().sn_icons, proper_name)
        if not self.name == proper_name:
            self.name = proper_name
        
    
    old_name: bpy.props.StringProperty()
    name: bpy.props.StringProperty(name="Name",
                                   description="The name of this variable",
                                   default="my_variable",
                                   update=update_name)
    
    def udpate_image(self,context):
        if self.image:
            self.image.preview.reload()

    image: bpy.props.PointerProperty(type=bpy.types.Image,
                                    update=udpate_image,
                                    name="Icon Image",
                                    description="Image for this icon")



class SN_UL_IconList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        if item.image:
            row.label(text="", icon_value=item.image.preview.icon_id)
        else:
            row.label(text="", icon="ERROR")
            
        row.prop(item,"name",emboss=False,text="")
