#SN_RunOperator

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python


class SN_EnumCollection(bpy.types.PropertyGroup):
    def get_items(self, context):
        items = []
        if self.identifier != "":
            for prop in eval(self.identifier):
                items.append((prop.identifier, prop.name, prop.description))
        return items

    identifier: bpy.props.StringProperty()
    prop_identifier: bpy.props.StringProperty()
    prop_name: bpy.props.StringProperty()
    enum: bpy.props.EnumProperty(items=get_items)

class SN_RunOperator(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunOperator"
    bl_label = "Run Operator"
    bl_icon = "CONSOLE"
    bl_width_default = 250
    node_color = (0.2, 0.2, 0.2)

    def update_name(self, context):
        self.enum_collection.clear()
        for inp in self.inputs:
            if inp.name != "Execute":
                self.inputs.remove(inp)

        if self.search_prop == "internal":
            if not self.propName in bpy.context.scene.sn_properties.operator_properties and self.propName != "":
                self.propName = ""
            elif self.propName in bpy.context.scene.sn_properties.operator_properties:
                #TODO add all identifiers
                identifiers = {"STRING": "STRING", "ENUM": "STRING","BOOLEAN": "BOOLEAN", "FLOAT": "FLOAT", "INT": "INTEGER"}
                for prop in eval("bpy.ops." + bpy.context.scene.sn_properties.operator_properties[self.propName].identifier + ".get_rna_type().bl_rna.properties"):
                    if prop.name != "RNA" and prop.type != "POINTER":
                        if prop.type == "ENUM":
                            item = self.enum_collection.add()
                            item.identifier = "bpy.ops." + bpy.context.scene.sn_properties.operator_properties[self.propName].identifier + ".get_rna_type().bl_rna.properties['" + prop.identifier + "'].enum_items"
                            item.prop_name = prop.name
                            item.prop_identifier = prop.identifier

                        elif prop.type == "FLOAT" or prop.type == "INT":
                            if prop.array_length > 1:
                                self.sockets.create_input(self, "VECTOR", prop.name)
                                self.inputs[-1].use_four_numbers = prop.array_length == 4
                            else:
                                self.sockets.create_input(self, identifiers[prop.type], prop.name).set_value(prop.default)
                                self.inputs[-1].value = prop.default

                        else:
                            self.sockets.create_input(self, identifiers[prop.type], prop.name).set_value(prop.default)

        else:
            if not self.propName in bpy.context.space_data.node_tree.custom_operator_properties and self.propName != "":
                self.propName = ""

    def update_enum(self, context):
        self.propName = ""
        if self.search_prop == "internal":
            if not len(bpy.context.scene.sn_properties.operator_properties):
                for category in dir(bpy.ops):
                    if category != "scripting_nodes" and not category[0].isnumeric():
                        for operator in dir(eval("bpy.ops."+category)):
                            if not operator[0].isnumeric():
                                if eval("bpy.ops."+category+"."+operator).get_rna_type().name and not eval("bpy.ops."+category+"."+operator).get_rna_type().name + " - " + category.replace("_"," ").title() in bpy.context.scene.sn_properties.operator_properties:
                                    item = bpy.context.scene.sn_properties.operator_properties.add()
                                    item.name = eval("bpy.ops."+category+"."+operator).get_rna_type().name + " - " + category.replace("_"," ").title()
                                    item.description = eval("bpy.ops."+category+"."+operator).get_rna_type().description
                                    item.identifier = category + "." + operator

    propName: bpy.props.StringProperty(name="Name", description="The name of the property", update=update_name)
    search_prop: bpy.props.EnumProperty(items=[("internal", "Internal", "Blenders internal properties"), ("custom", "Custom", "Your custom enums")], name="Properties", description="Which properties to display", update=update_enum)
    enum_collection: bpy.props.CollectionProperty(type=SN_EnumCollection)

    def inititialize(self,context):
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def draw_buttons(self, context, layout):
        layout.prop(self, "search_prop", expand=True)
        if self.search_prop == "internal":
            layout.prop_search(self,"propName",bpy.context.scene.sn_properties,"operator_properties",text="")
        else:
            layout.prop_search(self,"propName",bpy.context.space_data.node_tree,"custom_operator_properties",text="")

        if len(self.enum_collection):
            layout.separator(factor=1)
            box = layout.box()
            for prop in self.enum_collection:
                box.prop(prop, "enum", text=prop.prop_name)

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]

        execute = []
        if self.search_prop == "internal":
            if self.propName in bpy.context.scene.sn_properties.operator_properties:
                props = []
                for x, inp in enumerate(self.inputs):
                    if inp.name != "Execute":
                        for prop in eval("bpy.ops." + bpy.context.scene.sn_properties.operator_properties[self.propName].identifier + ".get_rna_type().bl_rna.properties"):
                            if prop.name == inp.name:
                                value = node_data["input_data"][x]["code"]
                                if inp.bl_idname == "SN_VectorSocket":
                                    if not inp.is_linked:
                                        if inp.use_four_numbers:
                                            value = str((inp.socket_value_quad[0], inp.socket_value_quad[1], inp.socket_value_quad[2], inp.socket_value_quad[3]))
                                        else:
                                            value = str((inp.socket_value[0], inp.socket_value[1], inp.socket_value[2]))

                                props+=[", " + prop.identifier + "=", value]

                for prop in self.enum_collection:
                    props+=[", " + prop.prop_identifier + "='", prop.enum + "'"]

                execute = ["bpy.ops." + bpy.context.scene.sn_properties.operator_properties[self.propName].identifier + "('INVOKE_DEFAULT'"] + props + [")"]
        else:
            if self.propName in bpy.context.space_data.node_tree.custom_operator_properties:
                execute = ["bpy.ops.scripting_nodes." + bpy.context.space_data.node_tree.custom_operator_properties[self.propName].name.lower().replace(" ", "_") + "('INVOKE_DEFAULT')"]

        return {
            "blocks": [
                {
                    "lines": [
                        execute
                    ],
                    "indented": []
                },
                {
                    "lines": [
                        [next_code]
                    ],
                    "indented": []
                }
            ],
            "errors": errors
        }

