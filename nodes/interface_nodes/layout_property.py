import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value, get_types
from ...node_sockets import update_socket_autocompile


class SN_UiPropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to use a property in a panel'''
    bl_idname = 'SN_UiPropertiesNode'
    bl_label = "Layout Property"
    bl_icon = node_icons["INTERFACE"]

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
        self.color = node_colors["INTERFACE"]

        self.outputs.new('SN_LayoutSocket', "Layout")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self, "propLocation")
        layout.prop(self, "propName")

    def evaluate(self,output):
        errors = []
        code = ""

        code+="bpy.context."
        code+=self.propLocation.lower()
        code+=", '"
        code+=self.propName

        return {"code":["_INDENT__INDENT_", self.outputs[0].links[0].to_node.layout_type(),
                        ".prop(", code, "')\n"], "error":errors}

