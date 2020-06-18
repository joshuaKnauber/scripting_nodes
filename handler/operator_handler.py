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

    def socket_idname_from_property_type(self, property_type):
        """ returns the  """

    def get_operator_properties(self,name):
        """ returns a list of properties for the given operator """
        operator = eval(self.get_ops_string(name))
        
        ignore_properties = ["RNA"]
        properties = []
        for operator_property in operator.get_rna_type().properties:
            if not operator_property.name in ignore_properties:
                properties.append((operator_property.name))
                print(operator_property.type)
        return properties