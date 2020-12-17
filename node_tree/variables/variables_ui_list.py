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



variable_icons = {
    "STRING": "SORTALPHA",
    "INTEGER": "LINENUMBERS_ON",
    "LIST": "PRESET"
}



class SN_Variable(bpy.types.PropertyGroup):

    def update_name(self,context):
        proper_name = re.sub(r'\W+', '', self.name.replace(" ","_"))
        if not proper_name:
            proper_name = "new_variable"
        if proper_name[0].isnumeric():
            proper_name = "var_"+proper_name
        proper_name = get_unique_name(self.node_tree.sn_variables, proper_name)
        if not self.name == proper_name:
            self.name = proper_name
    
    name: bpy.props.StringProperty(name="Name",
                                   description="The name of this variable",
                                   default="new_variable",
                                   update=update_name)

    node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree)

    def get_var_types(self,context):
        items = [("STRING","String","String",variable_icons["STRING"],0),
                 ("INTEGER","Integer","Integer",variable_icons["INTEGER"],1),
                 ("LIST","List","List",variable_icons["LIST"],2)]
        return items
    
    def update_var_type(self,context):
        self.make_property = False
    
    var_type: bpy.props.EnumProperty(items=get_var_types,
                                     update=update_var_type,
                                     name="Variable Type",
                                     description="The type of value that this variable can store")
    
    def update_make_property(self,context):
        self.attach_property_to = "Scene"
    
    make_property: bpy.props.BoolProperty(default=False,
                                          update=update_make_property,
                                        name="Make Property",
                                        description="Make this variable into a property that can be attached to ID objects")

    def get_attach_items(self,context):
        options = ["Action", "Armature", "Brush", "CacheFile", "Camera", "Collection", "Curve", "FreestyleLineStyle",
                   "GreasePencil", "Image", "Key", "Lattice", "Library", "Light", "LightProbe", "Mask", "Material",
                   "Mesh", "MetaBall", "MovieClip", "NodeTree", "Object", "PaintCurve", "Palette", "ParticleSettings",
                   "Scene", "Screen", "Sound", "Speaker", "Text", "Texture", "VectorFont", "Volume", "WindowManager",
                   "WorkSpace", "World"]
        items = []
        for option in options:
            items.append((option,option,option))
        return items
    
    attach_property_to: bpy.props.EnumProperty(items=get_attach_items,
                                               name="Attach To",
                                               description="This is the ID object which this property will be attached to")
    
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
