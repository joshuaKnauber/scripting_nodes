import bpy
from .error_handling import ErrorHandler

class CustomProperties():

    ErrorHandler = ErrorHandler()

    # CALLABLE FUNCTIONS
    # handle_layout_property: generates the custom properties for the layout property node
    # handle_change_property: generates the custom properties for the change property node
    # handle_data_properties: generates the custom properties for the data properties node

    def _get_nodes(self):
        """ gets all property nodes """

        property_nodes = []
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname == "SN_CreateProperty":
                property_nodes.append([node.propName, node.propDescription, node.propType, node.propLocation])
        
        return property_nodes

    def handle_layout_property(self, node, bpy_type):
        """ generates the custom properties for the layout property node """

        for item in node.sn_layout_property_properties:
            if item.isCustom:
                node.sn_layout_property_properties.remove(node.sn_layout_property_properties.find(item))

        for prop_node in self._get_nodes():
            if prop_node[3] == bpy_type:
                identifier = self.ErrorHandler.handle_text(prop_node[0])

                if not prop_node[0] in node.sn_layout_property_properties:
                    item = node.sn_layout_property_properties.add()
                    item.isCustom = True
                    identifier = self.ErrorHandler.handle_text(prop_node[0])

                    item.name = prop_node[0]
                    item.identifier = identifier
                    if prop_node[2] == "EnumProperty":
                        item.isEnum = True
                    elif prop_node[2] == "BoolProperty":
                        item.isBool = True

    def handle_change_property(self, node, bpy_type):
        """ generates the custom properties for the change property node """

        for item in node.sn_change_property_properties:
            if item.isCustom:
                node.sn_change_property_properties.remove(node.sn_change_property_properties.find(item))

        for prop_node in self._get_nodes():
            if prop_node[3] == bpy_type:
                identifier = self.ErrorHandler.handle_text(prop_node[0])

                if not prop_node[0] in node.sn_change_property_properties:
                    item = node.sn_change_property_properties.add()
                    item.name = prop_node[0]
                    item.identifier = identifier
                    item.isCustom = True
                    if prop_node[2] == "BoolProperty":
                        item.prop_type = "SN_BooleanSocket"

                    elif prop_node[2] == "StringProperty":
                        item.prop_type = "SN_StringSocket"

                    elif prop_node[2] == "FloatProperty":
                        item.prop_type = "SN_FloatSocket"

                    elif prop_node[2] == "IntProperty":
                        item.prop_type = "SN_IntSocket"

                    elif prop_node[2] == "EnumProperty":
                        item.prop_type = "SN_StringSocket"


    def handle_data_properties(self, node, bpy_type):
        """ generates the custom properties for the change property node """

        for item in node.search_properties:
            if item.isCustom:
                node.search_properties.remove(node.search_properties.find(item))

        for prop_node in self._get_nodes():
            if prop_node[3] == bpy_type:
                identifier = self.ErrorHandler.handle_text(prop_node[0])

                if not prop_node[0] in node.search_properties:
                    item = node.search_properties.add()
                    item.name = prop_node[0]
                    item.identifier = identifier
                    item.description = prop_node[1]
                    item.isCustom = True

                    if prop_node[2] == "BoolProperty":
                        item.type = str(bool)

                    elif prop_node[2] == "StringProperty":
                        item.type = str(str)

                    elif prop_node[2] == "FloatProperty":
                        item.type = str(float)

                    elif prop_node[2] == "IntProperty":
                        item.type = str(int)

                    elif prop_node[2] == "EnumProperty":
                        item.type = str(str)