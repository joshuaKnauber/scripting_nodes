import bpy
import re
from ..base_node import SN_ScriptingBaseNode


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
    "STRING": "SYNTAX_OFF",
    "INTEGER": "DRIVER_TRANSFORM",
    "FLOAT": "CON_TRANSLIKE",
    "BOOLEAN": "FORCE_CHARGE",
    "ENUM": "COLLAPSEMENU",
    "LIST": "PRESET",
    "BLEND_DATA": "MONKEY"
}



class SN_EnumItem(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name",
                                   description="The displayed name of your enum entry",
                                   default="My Item")
    
    description: bpy.props.StringProperty(name="Description",
                                   description="The tooltip of your enum entry",
                                   default="This is my enum item")



class SN_Variable(bpy.types.PropertyGroup):
    
    def find_node(self,context):
        for node in context.space_data.node_tree.nodes:
            if not node.bl_idname in ["NodeFrame","NodeReroute"]:
                if node.uid == self.from_node_uid:
                    return node
            
    def trigger_update(self,context):
        if self.use_self:
            node = self.find_node(context)
            node.update_from_collection(self.from_node_collection,self)

    def update_name(self,context):
        key = "variable"
        if self.is_property:
            key = "property"
            
        if not self.name:
            self.name = f"New {key.title()}"

        node = SN_ScriptingBaseNode()
        node.addon_tree = bpy.context.scene.sn.addon_tree()
        
        collection = self.node_tree.sn_variables
        if self.is_property:
            collection = self.node_tree.sn_properties
        if self.use_self:
            collection = getattr(self.find_node(context),self.from_node_collection)

        unique_name = node.get_unique_name(self.name, collection, " ")
        if unique_name != self.name:
            self.name = unique_name

        node.update_nodes_by_types("SN_GetVariableNode", "SN_SetVariableNode", "SN_AddToListNode",
                                   "SN_RemoveFromListNode", "SN_ChangeVariableNode", "SN_ResetVariableNode")

        self.identifier = node.get_python_name(self.name, f"new_{key}")

        node.update_nodes_by_types("SN_GetVariableNode", "SN_SetVariableNode", "SN_AddToListNode",
                                   "SN_RemoveFromListNode", "SN_ChangeVariableNode", "SN_ResetVariableNode")
        
        self.trigger_update(context)


    name: bpy.props.StringProperty(name="Name",
                                   description="The name of this variable",
                                   default="new_variable",
                                   update=update_name)
    
    identifier: bpy.props.StringProperty()

    node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree)
    
    use_self: bpy.props.BoolProperty(default=False)
    from_node_uid: bpy.props.StringProperty()
    from_node_collection: bpy.props.StringProperty()
    
    def get_var_types(self,context):
        if self.is_property:
            items = [("STRING","String","String",variable_icons["STRING"],0),
                    ("INTEGER","Integer","Integer",variable_icons["INTEGER"],1),
                    ("FLOAT","Float","Float",variable_icons["FLOAT"],2),
                    ("BOOLEAN","Boolean","Boolean",variable_icons["BOOLEAN"],3),
                    ("ENUM","Enum","Enum",variable_icons["ENUM"],4)]
        else:
            items = [("STRING","String","String",variable_icons["STRING"],0),
                    ("INTEGER","Integer","Integer",variable_icons["INTEGER"],1),
                    ("FLOAT","Float","Float",variable_icons["FLOAT"],2),
                    ("BOOLEAN","Boolean","Boolean",variable_icons["BOOLEAN"],3),
                    ("LIST","List","List",variable_icons["LIST"],4),
                    ("BLEND_DATA","Blend Data","Blend Data",variable_icons["BLEND_DATA"],5)]

        return items
    
    def update_var_type(self,context):
        self.make_property = False
        self.is_vector = False
        try: self.property_subtype = "NONE"
        except: self.property_subtype = "NO_SUBTYPES"
        try: self.property_unit = "NONE"
        except: self.property_unit = "NO_UNITS"

        node = SN_ScriptingBaseNode()
        node.addon_tree = bpy.context.scene.sn.addon_tree()
        node.update_nodes_by_types("SN_GetVariableNode", "SN_SetVariableNode", "SN_AddToListNode", "SN_RemoveFromListNode", "SN_ChangeVariableNode")

        self.trigger_update(context)


    var_type: bpy.props.EnumProperty(items=get_var_types,
                                     update=update_var_type,
                                     name="Variable Type",
                                     description="The type of value that this variable can store")

    description: bpy.props.StringProperty(name="Description",
                                        description="The description and tooltip of your property",
                                        update=trigger_update)
    
    def update_make_property(self,context):
        self.attach_property_to = "Scene"
    
    is_property: bpy.props.BoolProperty(default=False,
                                        update=update_make_property,
                                        name="Is Property",
                                        description="Make this variable into a property that can be attached to ID objects")
    
    is_vector: bpy.props.BoolProperty(default=False,
                                      name="Make Vector",
                                      description="Makes this property into a vector containing multiple of this property",
                                      update=trigger_update)
    
    vector_size: bpy.props.IntProperty(default=3,
                                       min=3,max=4,
                                       name="Vector Size",
                                       description="The size of the vector",
                                       update=trigger_update)
    
    def subtype_items(self,context):
        items = []
        if self.var_type == "STRING":
            subtypes = ['NONE', 'FILE_PATH', 'DIR_PATH', 'FILE_NAME', 'BYTE_STRING', 'PASSWORD']
        elif self.var_type == "INTEGER":
            if self.is_vector:
                subtypes = ['NONE', 'COLOR', 'TRANSLATION', 'DIRECTION', 'VELOCITY', 'ACCELERATION',
                            'MATRIX', 'EULER', 'QUATERNION', 'AXISANGLE', 'XYZ', 'XYZ_LENGTH',
                            'COLOR_GAMMA', 'COORDINATES', 'LAYER', 'LAYER_MEMBER']
            else:
                subtypes = ['NONE', 'PIXEL', 'UNSIGNED', 'PERCENTAGE', 'FACTOR', 'ANGLE', 'TIME',
                            'DISTANCE', 'DISTANCE_CAMERA', 'POWER', 'TEMPERATURE']
        elif self.var_type =="FLOAT":
            if self.is_vector:
                subtypes = ['NONE', 'COLOR', 'TRANSLATION', 'DIRECTION', 'VELOCITY', 'ACCELERATION',
                            'MATRIX', 'EULER', 'QUATERNION', 'AXISANGLE', 'XYZ', 'XYZ_LENGTH',
                            'COLOR_GAMMA', 'COORDINATES', 'LAYER', 'LAYER_MEMBER']
            else:
                subtypes = ['NONE', 'PIXEL', 'UNSIGNED', 'PERCENTAGE', 'FACTOR', 'ANGLE', 'TIME', 'DISTANCE',
                            'DISTANCE_CAMERA', 'POWER', 'TEMPERATURE']
        elif self.var_type == "BOOLEAN":
            if self.is_vector:
                subtypes = ['NONE', 'COLOR', 'TRANSLATION', 'DIRECTION', 'VELOCITY', 'ACCELERATION',
                            'MATRIX', 'EULER', 'QUATERNION', 'AXISANGLE', 'XYZ', 'XYZ_LENGTH',
                            'COLOR_GAMMA', 'COORDINATES', 'LAYER', 'LAYER_MEMBER']
            else:
                subtypes = ["NO_SUBTYPES"]
        else:
            subtypes = ["NO_SUBTYPES"]
        for subtype in subtypes:
            items.append((subtype,subtype.replace("_"," ").title(),subtype.replace("_"," ").title()))
        return items
        
    property_subtype: bpy.props.EnumProperty(items=subtype_items,
                                             name="Subtype",
                                             description="The subtype of this property",
                                             update=trigger_update)

    property_options: bpy.props.EnumProperty(items=[("HIDDEN", "Hide", "Hide in operator edit popup (Shift-Click to select multiple)"), ("SKIP_SAVE", "Skip Save", "Don't save this property for the next time the operator is called (Shift-Click to select multiple)"), ("ANIMATABLE", "Animatable", "Defines if this property is animatable (Shift-Click to select multiple)")], name="Options", description="Property options", options={"ENUM_FLAG"})


    def unit_items(self, context):
        units = ["NONE", "LENGTH", "AREA", "VOLUME", "ROTATION", "TIME", "VELOCITY",
                 "ACCELERATION", "MASS", "CAMERA", "POWER"]
        if self.var_type in ["STRING","ENUM","INTEGER","BOOLEAN"]:
            units = ["NO_UNITS"]
        items = []
        for unit in units:
            items.append((unit,unit.title(),unit.title()))
        return items
    
    property_unit: bpy.props.EnumProperty(items=unit_items,
                                          name="Unit",
                                          description="The unit of this property",
                                          update=trigger_update)

    def get_attach_items(self,context):
        options = ["Action", "Armature", "Brush", "CacheFile", "Camera", "Collection", "Curve", "FreestyleLineStyle",
                   "GreasePencil", "Image", "Key", "Lattice", "Library", "Light", "LightProbe", "Mask", "Material",
                   "Mesh", "MetaBall", "MovieClip", "NodeTree", "Object", "Palette", "ParticleSettings",
                   "Scene", "Screen", "Sound", "Speaker", "Text", "Texture", "Volume", "WindowManager",
                   "WorkSpace", "World"]
        items = []
        for option in options:
            items.append((option,option,option))
        return items
    
    is_data_collection: bpy.props.BoolProperty(name="Data Collection",
                                               description="Holds a data collection instead of a single data block",
                                               update=update_var_type)
    
    attach_property_to: bpy.props.EnumProperty(items=get_attach_items,
                                               name="Attach To",
                                               description="This is the ID object which this property will be attached to",
                                               update=trigger_update)
    
    str_default: bpy.props.StringProperty(default="",
                                        name="Default Value",
                                        description="The default value of this variable",
                                        update=trigger_update)
    
    use_min: bpy.props.BoolProperty(default=False,
                                    name="Use Min",
                                    description="Give a minimum value for the property",
                                    update=trigger_update)
    
    use_max: bpy.props.BoolProperty(default=False,
                                    name="Use Max",
                                    description="Give a maximum value for the property",
                                    update=trigger_update)
    
    use_soft_min: bpy.props.BoolProperty(default=False,
                                         name="Use Soft Min",
                                         description="Use a soft minimum which can be overwritten by typing a value",
                                        update=trigger_update)
    
    use_soft_max: bpy.props.BoolProperty(default=False,
                                         name="Use Soft Max",
                                         description="Use a soft maximum which can be overwritten by typing a value",
                                        update=trigger_update)
    
    int_default: bpy.props.IntProperty(default=0,
                                        name="Default Value",
                                        description="The default value of this variable",
                                        update=trigger_update)
    
    int_three_default: bpy.props.IntVectorProperty(default=(0,0,0),
                                                   size=3,
                                                    name="Default Value",
                                                    description="The default value of this variable",
                                                    update=trigger_update)
    
    int_four_default: bpy.props.IntVectorProperty(default=(0,0,0,0),
                                                    size=4,
                                                    name="Default Value",
                                                    description="The default value of this variable",
                                                    update=trigger_update)
    
    int_min: bpy.props.IntProperty(default=0,
                                   name="Minimum",
                                   description="The minimum value this property can go to",
                                    update=trigger_update)
    
    int_max: bpy.props.IntProperty(default=1,
                                   name="Maximum",
                                   description="The maximum value this property can go to",
                                    update=trigger_update)
    
    int_soft_min: bpy.props.IntProperty(default=0,
                                   name="Soft Minimum",
                                   description="A soft minimum value which can be overwritten by typing",
                                    update=trigger_update)
    
    int_soft_max: bpy.props.IntProperty(default=1,
                                   name="Soft Maximum",
                                   description="A soft maximum value which can be overwritten by typing",
                                    update=trigger_update)
    
    float_default: bpy.props.FloatProperty(default=0,
                                        name="Default Value",
                                        description="The default value of this variable",
                                        update=trigger_update)
    
    float_three_default: bpy.props.FloatVectorProperty(default=(0,0,0),
                                                   size=3,
                                                    name="Default Value",
                                                    description="The default value of this variable",
                                                    update=trigger_update)
    
    float_four_default: bpy.props.FloatVectorProperty(default=(0,0,0,0),
                                                    size=4,
                                                    name="Default Value",
                                                    description="The default value of this variable",
                                                    update=trigger_update)
    
    float_min: bpy.props.FloatProperty(default=0,
                                   name="Minimum",
                                   description="The minimum value this property can go to",
                                    update=trigger_update)
    
    float_max: bpy.props.FloatProperty(default=1,
                                   name="Maximum",
                                   description="The maximum value this property can go to",
                                    update=trigger_update)
    
    float_soft_min: bpy.props.FloatProperty(default=0,
                                   name="Soft Minimum",
                                   description="A soft minimum value which can be overwritten by typing",
                                    update=trigger_update)
    
    float_soft_max: bpy.props.FloatProperty(default=1,
                                   name="Soft Maximum",
                                   description="A soft maximum value which can be overwritten by typing",
                                    update=trigger_update)
    
    bool_default: bpy.props.BoolProperty(default=True,
                                        name="Default Value",
                                        description="The default value of this variable",
                                        update=trigger_update)
    
    bool_three_default: bpy.props.BoolVectorProperty(default=(True,True,True),
                                                   size=3,
                                                    name="Default Value",
                                                    description="The default value of this variable",
                                                    update=trigger_update)
    
    bool_four_default: bpy.props.BoolVectorProperty(default=(True,True,True,True),
                                                    size=4,
                                                    name="Default Value",
                                                    description="The default value of this variable",
                                                    update=trigger_update)
    
    enum_items: bpy.props.CollectionProperty(type=SN_EnumItem)
    
    def enum_string(self):
        items = "["
        for item in self.enum_items:
            items += f"(\"{item.name}\",\"{item.name}\",\"{item.description}\"),"
        return items + "]"
    
    def property_default(self):
        if self.var_type == "STRING":
            return f"default='{self.str_default}'"
        elif self.var_type == "INTEGER":
            if self.is_vector:
                if self.vector_size == 3:
                    return "default="+str(tuple(self.int_three_default)) + ",size=3"
                return "default="+str(tuple(self.int_four_default)) + ",size=4"
            return "default="+str(self.int_default)
        elif self.var_type == "FLOAT":
            if self.is_vector:
                if self.vector_size == 3:
                    return "default="+str(tuple(self.float_three_default)) + ",size=3"
                return "default="+str(tuple(self.float_four_default)) + ",size=4"
            return "default="+str(self.float_default)
        elif self.var_type == "BOOLEAN":
            if self.is_vector:
                if self.vector_size == 3:
                    return "default="+str(tuple(self.bool_three_default)) + ",size=3"
                return "default="+str(tuple(self.bool_four_default)) + ",size=4"
            return "default="+str(self.bool_default)
        elif self.var_type == "ENUM":
            items = []
            for item in self.enum_items:
                items.append((item.name,item.name,item.description))
            if not items:
                items = [("None","None","None")]
            return "items="+str(items)
        
    def property_min_max(self):
        min_max = ""
        if self.var_type == "INTEGER":
            if self.use_min: min_max += ",min="+str(self.int_min)
            if self.use_max: min_max += ",max="+str(self.int_max)
            if self.use_soft_min: min_max += ",soft_min="+str(self.int_soft_min)
            if self.use_soft_max: min_max += ",soft_max="+str(self.int_soft_max)
        elif self.var_type == "FLOAT":
            if self.use_min: min_max += ",min="+str(self.float_min)
            if self.use_max: min_max += ",max="+str(self.float_max)
            if self.use_soft_min: min_max += ",soft_min="+str(self.float_soft_min)
            if self.use_soft_max: min_max += ",soft_max="+str(self.float_soft_min)
        return min_max
    
    def property_register(self):
        prop_names = {"STRING":"String","INTEGER":"Int","FLOAT":"Float","BOOLEAN":"Bool","ENUM":"Enum"}
        if self.use_self:
            property_line = f"{self.identifier} : bpy.props.{prop_names[self.var_type]}"
        else:
            property_line = f"bpy.types.{self.attach_property_to}.{self.identifier} = bpy.props.{prop_names[self.var_type]}"
        property_line += f"{'Vector' if self.is_vector else ''}Property("
        property_line += f"name='{self.name}',description='{self.description}',"
        if self.property_subtype != "NO_SUBTYPES":
            property_line += f"subtype='{self.property_subtype}',"
        if self.property_unit != "NO_UNITS":
            property_line += f"unit='{self.property_unit}',"
        property_line += f"options={self.property_options},"
        property_line += f"{self.property_default()}"
        property_line += f"{self.property_min_max()})\n"
        return property_line
    
    def property_unregister(self):
        return f"del bpy.types.{self.attach_property_to}.{self.identifier}\n"

    def get_variable_default(self):
        value = "[]"
        if self.var_type == "STRING":
            value = f'"{self.str_default}"'
        elif self.var_type == "INTEGER":
            value = str(self.int_default)
        elif self.var_type == "FLOAT":
            value = str(self.float_default)
        elif self.var_type == "BOOLEAN":
            value = str(self.bool_default)
        elif self.var_type == "BLEND_DATA" and not self.is_data_collection:
            value = "None"

        return value

    def variable_register(self):
        return f""""{self.identifier}": {self.get_variable_default()}, """


class SN_UL_VariableList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text="", icon= variable_icons[item.var_type])
        row.prop(item,"name",emboss=False,text="")
