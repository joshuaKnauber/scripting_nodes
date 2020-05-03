import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value, get_types
from ...node_sockets import update_socket_autocompile


class SN_SetPropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to get the value of a properties'''
    bl_idname = 'SN_SetPropertiesNode'
    bl_label = "Change Property"
    bl_icon = node_icons["OPERATOR"]

    def getTypes(self, context):
        types = get_types()

        newTypes = []
        for typeName in types:
            newTypes.append((typeName, typeName, ""))
        
        return newTypes

    def getNames(self, context):
        names = []
        location = self.propLocation

        dontDisplay = ["sn_properties", "sn_error_properties", "RNA"]
        for node in context.space_data.node_tree.nodes:
            if node.bl_idname == "SN_PropertiesNode":
                if node.propLocation == location:
                    dontDisplay.append(node.propName)
                    newName = node.propName
                    newName = newName.lower()
                    newName = newName.replace(" ", "_")
                    names.append((newName, node.propName, ""))

        for prop in eval("bpy.types." + location + ".bl_rna.properties"):
            if not prop.name in dontDisplay:
                newName = prop.name
                newName = newName.lower()
                newName = newName.replace(" ", "_")
                names.append((newName, prop.name, ""))

        return names


    propLocation: bpy.props.EnumProperty(items=getTypes, name="Location", description="", default=None, update=update_socket_autocompile, get=None, set=None)
    propName: bpy.props.EnumProperty(items=getNames, name="Name", description="", default=None, update=update_socket_autocompile)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        self.inputs.new('SN_ProgramSocket', "Program")
        self.inputs.new('SN_DataSocket', "Value")
        self.outputs.new('SN_ProgramSocket', "Program")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self, "propLocation")
        layout.prop(self, "propName")

    def evaluate(self,output):
        errors = []
        code = []

        code.append("bpy.data.materials")
        code.append("[0].")
        #code.append(self.propLocation)
        code.append(str(self.propName))
        code.append(" = ")
        if not self.inputs[1].is_linked:
            errors.append("no_connection")
            code.append("False")
            code.append("\n")
            return {"code": code, "error": errors}
        else:
            return {"code": [code, self.inputs[1].links[0].from_socket, "\n"]}
