import bpy


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



variable_icons = {
    "String": "SORTALPHA",
    "Integer": "LINENUMBERS_ON",
    "List": "PRESET"
}



class SN_Variable(bpy.types.PropertyGroup):

    def update_name(self,context):
        unique_name = get_unique_name(self.node_tree.sn_variables, self.name)
        if not self.name == unique_name:
            self.name = unique_name
    
    name: bpy.props.StringProperty(name="Name",
                                   description="The name of this variable",
                                   default="my_variable",
                                   update=update_name)

    node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree)

    def get_var_types(self,context):
        items = [("String","String","String",variable_icons["String"],0),
                 ("Integer","Integer","Integer",variable_icons["Integer"],1),
                 ("List","List","List",variable_icons["List"],2)]
        return items
    
    var_type: bpy.props.EnumProperty(items=get_var_types,
                                     name="Variable Type",
                                     description="The type of value that this variable can store")
    
    str_default: bpy.props.StringProperty(default="",
                                        name="Default Value",
                                        description="The default value of this variable")
    
    int_default: bpy.props.IntProperty(default=0,
                                        name="Default Value",
                                        description="The default value of this variable")



class SN_UL_VariableList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text="", icon= variable_icons[item.var_type])
        row.prop(item,"name",emboss=False,text="")
