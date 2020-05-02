import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value
from ...node_sockets import update_socket_autocompile

# boolean
# string
# float
# int
# enum

#   choose thing
# give name (name=)
# give description
#   assign to type

class SN_PropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to create a properties'''
    bl_idname = 'SN_PropertiesNode'
    bl_label = "Property"
    bl_icon = node_icons["OPERATOR"]
    bl_width_default = 300

    propName: bpy.props.StringProperty(name="Name", description="Name of the property", default="My Property", update=update_socket_autocompile)
    propDescription: bpy.props.StringProperty(name="Description", description="Description of the property", default="My Description", update=update_socket_autocompile)
    propType: bpy.props.EnumProperty(items=[("BoolProperty", "Boolean", "A boolean input"), ("EnumProperty", "List", "A dropdown list that can be converted to display all values"), ("FloatProperty", "Numbers", "A input for all numbers"), ("IntProperty", "Whole Numbers", "A input for whole numbers"), ("StringProperty", "Text", "A text input")], name="Type", description="", default=None, update=update_socket_autocompile, get=None, set=None)
    
    def getTypes(self, context):
        types = ["Scene", "Object", "Material"]

        newTypes = []
        for typeName in types:
            newTypes.append((typeName, typeName, ""))
        
        return newTypes
    
    propLocation: bpy.props.EnumProperty(items=getTypes, name="Location", description="", default=None, update=update_socket_autocompile, get=None, set=None)


    propBool: bpy.props.EnumProperty(items=[("True", "True", ""), ("False", "False", "")], name="Default", description="The default value", update=update_socket_autocompile)
    propString: bpy.props.StringProperty(name="", description="The default value", default="Default", update=update_socket_autocompile)
    propFloat: bpy.props.FloatProperty(name="", description="The default value", default=0.0, update=update_socket_autocompile)
    propInt: bpy.props.IntProperty(name="", description="The default value", default=0, update=update_socket_autocompile)
    propEnum: bpy.props.StringProperty(name="", description="The default value", update=update_socket_autocompile)


    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        pIn = self.inputs.new('SN_ProgramSocket', "Program")
        pIn.display_shape = "DIAMOND"

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"propType")
        layout.prop(self,"propLocation")
        layout.prop(self,"propName")
        layout.prop(self,"propDescription")
        if self.propType == "BoolProperty":
            layout.label(text="Default:")
            layout.prop(self, "propBool", expand=True)
        elif self.propType == "StringProperty":
            layout.label(text="Default:")
            layout.prop(self, "propString")
        elif self.propType == "FloatProperty":
            layout.label(text="Default:")
            layout.prop(self, "propFloat")
        elif self.propType == "IntProperty":
            layout.label(text="Default:")
            layout.prop(self, "propInt")
        elif self.propType == "EnumProperty":
            layout.label(text="Items (Seperate Items with commas):")
            layout.prop(self, "propEnum")

    def evaluate(self,output):
        errors = []
        code = []

        newPropName = self.propName.replace(" ","_")
        newPropName = newPropName.lower()

        code.append("bpy.types.")
        code.append(self.propLocation)
        code.append(".")
        code.append(newPropName)
        code.append(" = bpy.props.")
        code.append(self.propType)
        code.append("(name='")
        code.append(self.propName)
        code.append("', description='")
        code.append(self.propDescription)

        if self.propType == "BoolProperty":
            code.append("', default=")
            code.append(self.propBool)
            code.append(")")

        elif self.propType == "StringProperty":
            code.append("', default='")
            code.append(self.propString)
            code.append("')")

        elif self.propType == "FloatProperty":
            code.append("', default=")
            code.append(str(self.propFloat))
            code.append(")")

        elif self.propType == "IntProperty":
            code.append("', default=")
            code.append(str(self.propInt))
            code.append(")")

        elif self.propType == "EnumProperty":
            code.append("', items=")
            items = self.propEnum.split(",")
            newItems=[]
            for item in items:
                item = item.strip()
                newItemName = item.replace(" ","_")
                newItemName = newItemName.lower()
                newItems.append((newItemName, item, ""))
            code.append(str(newItems))
            code.append(")")

        code.append("\n")
        return {"code": code, "error":errors}
