import bpy

class SN_OperatorProperties(bpy.types.PropertyGroup):

    # name of the operator
    name: bpy.props.StringProperty(default="", name="Name", description="Name of the operator")

    # name of the operator
    description: bpy.props.StringProperty(default="", name="Description", description="Description of the operator")

    # name of the operator
    identifier: bpy.props.StringProperty(default="", name="Identifier", description="Identifier of the operator")
    
    # category of the operator
    category: bpy.props.StringProperty(default="", name="Category", description="Category of the operator")


class OperatorHandler():

    enum_item_cache = {}

    def get_operator_categories(self):
        """ returns a list with all operator categories as items """
        items = []
        for categorie in dir(bpy.ops):
            name = categorie.replace("_"," ").title()
            items.append((categorie,name,name + " operators"))
        return items

    def set_operator_items(self,category,operator_property):
        """ adds the operators to the given collection property """
        added_names = []
        for operator in dir(eval("bpy.ops."+category)):
            if not operator in added_names:
                if eval("bpy.ops."+category+"."+operator).get_rna_type().name:
                    item = operator_property.add()
                    item.name = eval("bpy.ops."+category+"."+operator).get_rna_type().name + " - " + category.replace("_"," ").title()
                    item.description = eval("bpy.ops."+category+"."+operator).get_rna_type().name
                    item.identifier = eval("bpy.ops."+category+"."+operator).get_rna_type().name
                    item.category = category
                    added_names.append(operator)

    def get_ops_string(self,name):
        """ returns the operator string for the given operator name """
        for category in self.get_operator_categories():
            category = category[0]
            for operator in dir(eval("bpy.ops."+category)):
                if eval("bpy.ops."+category+"."+operator).get_rna_type().name + " - " + category.replace("_"," ").title() == name:
                    return "bpy.ops."+category+"."+operator

    def set_scene_operators(self):
        """ adds all operators to the scene collection """
        bpy.context.scene.sn_operators.clear()
        for category in self.get_operator_categories():
            self.set_operator_items(category[0],bpy.context.scene.sn_operators)

    def socket_idname_from_property_type(self, property_type, array):
        """ returns the socket id name from the property type """
        if property_type in ["FLOAT"]:
            if not array:
                return "SN_FloatSocket"
            else:
                return "SN_VectorSocket"
        elif property_type in ["INT"]:
            if not array:
                return "SN_IntSocket"
            else:
                return "SN_VectorSocket"
        elif property_type in ["STRING"]:
            return "SN_StringSocket"
        elif property_type in ["BOOLEAN"]:
            return "SN_BooleanSocket"
        elif property_type in ["ENUM"]:
            return "SN_EnumSocket"
        else:
            return "SN_DataSocket"

    def get_operator_properties(self,name):
        """ returns a list of properties for the given operator """
        operator = self.get_ops_string(name)
        properties = []
        if operator:
            operator = eval(operator)
            
            ignore_properties = ["RNA"]
            for operator_property in operator.get_rna_type().properties:
                if not operator_property.name in ignore_properties:
                    array = False
                    if operator_property.type in ["INT","FLOAT"]:
                        array = operator_property.array_length > 1
                    properties.append((operator_property.name, self.socket_idname_from_property_type(operator_property.type, array), operator_property))
        return properties

    def get_enum_items(self, op_name, prop_name):
        """ returns the enum items for the given property """
        key = op_name + " - " + prop_name
        if not key in self.enum_item_cache:
            for op_prop in self.get_operator_properties(op_name):
                if op_prop[0] == prop_name:
                    items = []
                    for item in op_prop[2].enum_items:
                        items.append((item.identifier,item.name,item.description))
                    self.enum_item_cache[key] = items
                    return items
            self.enum_item_cache[key] = []
            return []
        else:
            return self.enum_item_cache[key]

    def get_property_identifier(self, op_name, prop_name):
        """ returns the identifier of the given property """
        for op_prop in self.get_operator_properties(op_name):
            if op_prop[0] == prop_name:
                return op_prop[2].identifier
        return ""