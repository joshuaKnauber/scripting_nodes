#SN_RunOperator

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python


def create_internal_ops():
    if not len(bpy.context.scene.sn_properties.operator_properties):
        for category in dir(bpy.ops):
            if category != "scripting_nodes" and not category[0].isnumeric():
                for operator in dir(eval("bpy.ops."+category)):
                    if not operator[0].isnumeric():
                        op = eval("bpy.ops."+category+"."+operator).get_rna_type()
                        # name = op.name
                        name = op.identifier.split("_OT_")[-1].replace("_"," ").title()
                        if name and not name + " - " + category.replace("_"," ").title() in bpy.context.scene.sn_properties.operator_properties:
                            item = bpy.context.scene.sn_properties.operator_properties.add()
                            item.name = name + " - " + category.replace("_"," ").title()
                            item.description = eval("bpy.ops."+category+"."+operator).get_rna_type().description
                            item.identifier = category + "." + operator


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
    bl_icon = "SEQ_CHROMA_SCOPE"
    bl_width_default = 250
    node_color = (0.2, 0.2, 0.2)

    docs = {
        "text": ["This node is used to <important>run an operator</>.",
                "Internal/Custom: <subtext>Here you can select if you want to use operators you create in this addon or blenders internal ones</>"
                ""],
        "python": ["bpy.ops.screen.userpref_show()"]

    }

    def update_name_external(self):
        if self.search_prop == "custom":
            for op in bpy.context.space_data.node_tree.custom_operator_properties:
                if op.identifier == self.op_uid:
                    self.propName = op.name

    def update_name(self, context):
        self.enum_collection.clear()
        for inp in self.inputs:
            if inp.name != "Execute":
                self.inputs.remove(inp)

        if self.search_prop == "internal":
            if not self.propName in bpy.context.scene.sn_properties.operator_properties and self.propName != "":
                self.propName = ""
            elif self.propName in bpy.context.scene.sn_properties.operator_properties:
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
                                socket = self.sockets.create_input(self, "VECTOR", prop.name)
                                socket.use_four_numbers = prop.array_length == 4
                                socket.is_color = prop.name == "Color"
                                # socket.is_color = prop.subtype == "COLOR"
                            else:
                                if prop.type in identifiers:
                                    self.sockets.create_input(self, identifiers[prop.type], prop.name).set_value(prop.default)
                                    self.inputs[-1].value = prop.default

                        else:
                            if prop.type in identifiers:
                                self.sockets.create_input(self, identifiers[prop.type], prop.name).set_value(prop.default)

        else:
            if not self.propName in bpy.context.space_data.node_tree.custom_operator_properties and self.propName != "":
                self.propName = ""
                self.op_uid = ""
            elif self.propName != "":
                self.op_uid = bpy.context.space_data.node_tree.custom_operator_properties[self.propName].identifier

    def update_enum(self, context):
        self.propName = ""
        if self.search_prop == "internal":
            create_internal_ops()

    op_uid: bpy.props.StringProperty()
    propName: bpy.props.StringProperty(name="Name", description="The name of the property", update=update_name)
    search_prop: bpy.props.EnumProperty(items=[("internal", "Internal", "Blenders internal properties"), ("custom", "Custom", "Your custom enums")], name="Properties", description="Which properties to display", update=update_enum)
    enum_collection: bpy.props.CollectionProperty(type=SN_EnumCollection)

    use_invoke: bpy.props.BoolProperty(default=True,name="Show Popups",description="Shows confirm and other popups. Might cause issues if not enabled for internal operators.")

    def inititialize(self,context):
        self.update_enum(None)
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def draw_buttons(self, context, layout):
        layout.prop(self, "search_prop", expand=True)
        if self.search_prop == "internal":
            layout.prop_search(self,"propName",bpy.context.scene.sn_properties,"operator_properties",text="")
        else:
            layout.prop_search(self,"propName",bpy.context.space_data.node_tree,"custom_operator_properties",text="")

        layout.prop(self,"use_invoke")

        if len(self.enum_collection):
            layout.separator(factor=1)
            box = layout.box()
            for prop in self.enum_collection:
                box.prop(prop, "enum", text=prop.prop_name)

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]

        invoke = "'EXEC_DEFAULT'"
        if self.use_invoke:
            invoke = "'INVOKE_DEFAULT'"

        execute = ["pass"]
        if self.search_prop == "internal":
            if self.propName in bpy.context.scene.sn_properties.operator_properties:
                props = []
                for x, inp in enumerate(self.inputs):
                    if inp.name != "Execute":
                        for prop in eval("bpy.ops." + bpy.context.scene.sn_properties.operator_properties[self.propName].identifier + ".get_rna_type().bl_rna.properties"):
                            if prop.name == inp.name:
                                props+=[", " + prop.identifier + "=", node_data["input_data"][x]["code"]]

                for prop in self.enum_collection:
                    props+=[", " + prop.prop_identifier + "='", prop.enum + "'"]

                execute = ["bpy.ops." + bpy.context.scene.sn_properties.operator_properties[self.propName].identifier + "("+invoke+""] + props + [")"]
        else:
            if self.propName in node_data["node_tree"].custom_operator_properties:
                execute = ["bpy.ops.scripting_nodes.sna_ot_operator_" + node_data["node_tree"].custom_operator_properties[self.propName].identifier.lower() + "("+invoke+")"]

        return {"blocks": [{"lines": [execute],"indented": []},{"lines": [[next_code]],"indented": []}],"errors": errors}

