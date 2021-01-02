import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup
from ...node_tree.variables.variables_ui_list import SN_Variable
from ...interface.sidepanel.graph_panels import draw_property


class SN_OT_AddOperatorProperty(bpy.types.Operator):
    bl_idname = "sn.add_operator_property"
    bl_label = "Add Operator Property"
    bl_description = "Adds a new property to this operator"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_name: bpy.props.StringProperty()

    def execute(self, context):
        addon_tree = context.space_data.node_tree
        node = addon_tree.nodes[self.node_name]

        variable = node.operator_properties.add()
        variable.is_property = True
        variable.use_self = True
        variable.node_tree = addon_tree
        variable.name = "New Property"
        node.property_index = len(node.operator_properties)-1

        return {"FINISHED"}


class SN_OT_RemoveOperatorProperty(bpy.types.Operator):
    bl_idname = "sn.remove_operator_property"
    bl_label = "Remove Operator Property"
    bl_description = "Remove a property from this operator"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_name: bpy.props.StringProperty()

    def execute(self, context):
        addon_tree = context.space_data.node_tree
        node = addon_tree.nodes[self.node_name]

        node.operator_properties.remove(node.property_index)
        if len(node.operator_properties):
            node.property_index = len(node.operator_properties)-1
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class SN_OT_EditOperatorProperty(bpy.types.Operator):
    bl_idname = "sn.edit_operator_property"
    bl_label = "Edit Operator Property"
    bl_description = "Edit a property from this operator"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_name: bpy.props.StringProperty()

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        addon_tree = context.space_data.node_tree
        node = addon_tree.nodes[self.node_name]
        variable = node.operator_properties[node.property_index]
        draw_property(context, variable, self.layout)


class SN_OperatorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_OperatorNode"
    bl_label = "Operator"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "has_collection": True,
    }

    def update_name(self, context):
        self["operator_name"] = self.operator_name.replace("\"", "'")
        if not self.operator_name:
            self.operator_name = "New Operator"

        self.item.name = self.operator_name
        self.item.identifier = self.get_python_name(self.operator_name, "new_operator")

        unique_name = self.get_unique_name(self.operator_name, self.collection.items, " ")
        if unique_name != self.operator_name:
            self.operator_name = unique_name
        
        self.item.name = self.operator_name
        self.item.identifier = self.get_python_name(self.operator_name, "new_operator")
        self.update_needs_compile(context)

    def update_description(self, context):
        self["operator_description"] = self.operator_description.replace("\"", "'")
        self.item.description = self.operator_description.replace("\"", "'")

    def update_popup(self,context):
        if len(self.inputs) != 2:
            self.add_integer_input("Width").set_default(300)
        if self.outputs[0].name != "Operator":
            self.add_execute_output("Operator")
            self.outputs.move(len(self.outputs)-1, 0)
        if len(self.outputs) < 3:
            self.add_dynamic_interface_output("Popup")


        if self.invoke_option in ["none", "invoke_confirm"]:
            self.inputs.remove(self.inputs[1])
            for i, out in enumerate(self.outputs):
                if i > 1:
                    self.outputs.remove(out)
        elif self.invoke_option == "invoke_popup":
            self.outputs.remove(self.outputs[0])
        elif self.invoke_option == "invoke_props_popup":
            self.inputs.remove(self.inputs[1])


    operator_name: bpy.props.StringProperty(name="Name", description="Name of the operator", update=update_name)
    operator_description: bpy.props.StringProperty(name="Description", description="Description of the operator", update=update_description)
    invoke_option: bpy.props.EnumProperty(name="Popup",items=[("none","None","None"),("invoke_confirm","Confirm","You need to confirm the operator"),("invoke_props_dialog","Property Dialog","Opens a customizable property dialog"), ("invoke_popup", "Popup", "Shows a customizable popup"), ("invoke_props_popup", "Property Popup", "Show operator properties and execute it automatically on changes"), ("invoke_search_popup", "Search Popup", "Opens a search menu from an enum property")],update=update_popup)
    operator_properties: bpy.props.CollectionProperty(type=SN_Variable)
    property_index: bpy.props.IntProperty()

    def on_create(self,context):
        self.add_execute_output("Operator")
        self.add_execute_output("Invoke")
        self.add_boolean_input("Poll")
        self.update_name(None)


    def draw_node(self,context,layout):
        layout.prop(self, "operator_name")
        layout.label(text="Description: ")
        layout.prop(self, "operator_description", text="")
        layout.prop(self, "invoke_option")

        row = layout.row(align=False)
        row.template_list("SN_UL_VariableList", "Properties", self, "operator_properties", self, "property_index",rows=3)
        col = row.column(align=True)
        col.operator("sn.add_operator_property", text="", icon="ADD").node_name = self.name
        col = col.column(align=True)
        col.enabled = bool(len(self.operator_properties))
        col.operator("sn.remove_operator_property", text="", icon="REMOVE").node_name = self.name
        col.operator("sn.edit_operator_property", text="", icon="GREASEPENCIL").node_name = self.name


    def what_layout(self, socket):
        return "layout"


    def code_imperative(self, context):
        property_register = []
        for prop in self.operator_properties:
            property_register.append(prop.property_register() + "\n")

        if not self.invoke_option in ["invoke_popup", "invoke_search_popup"]:
            layouts = []
            if self.outputs[-1].sn_type == "DYNAMIC":
                for out in self.outputs[2:-1]:
                    layouts.append(out.block(0))


            return_invoke = """self.execute(context)"""
            if self.invoke_option != "none":
                return_invoke = "context.window_manager." + self.invoke_option
            if self.invoke_option == "invoke_confirm":
                return_invoke += "(self, event)"
            elif self.invoke_option == "invoke_props_dialog":
                return_invoke += f"(self, width={self.inputs[1].value})"
            elif self.invoke_option == "invoke_props_popup":
                return_invoke += "(self, event)"


            return {
                "code": f"""
                        class SNA_OT_{self.item.identifier.title()}(bpy.types.Operator):
                            bl_idname = "sna.{self.item.identifier}"
                            bl_label = "{self.item.name}"
                            bl_description = "{self.item.description}"
                            bl_options = {"{" + '"REGISTER", "UNDO"' + "}"}

                            {self.list_blocks(property_register, 7)}

                            @classmethod
                            def poll(cls, context):
                                return {self.inputs[0].value}

                            def execute(self, context):
                                {self.outputs[0].block(8)}
                                return {{"FINISHED"}}

                            def invoke(self, context, event):
                                {self.outputs[1].block(8)}
                                return {return_invoke}

                            def draw(self, context):
                                layout = self.layout
                                {self.list_blocks(layouts, 8)}
                        """
            }

        elif self.invoke_option == "invoke_popup":
            layouts = []
            if self.outputs[-1].sn_type == "DYNAMIC":
                for out in self.outputs[1:-1]:
                    layouts.append(out.block(0))

            return {
                "code": f"""
                        class SNA_OT_{self.item.identifier.title()}(bpy.types.Operator):
                            bl_idname = "sna.{self.item.identifier}"
                            bl_label = "{self.item.name}"
                            bl_description = "{self.item.description}"
                            bl_options = {"{" + '"REGISTER", "UNDO"' + "}"}

                            {self.list_blocks(property_register, 7)}

                            @classmethod
                            def poll(cls, context):
                                return {self.inputs[0].value}

                            def execute(self, context):
                                return {{"FINISHED"}}

                            def invoke(self, context, event):
                                {self.outputs[0].block(8)}
                                return context.window_manager.invoke_popup(self, width={self.inputs[1].value})

                            def draw(self, context):
                                layout = self.layout
                                {self.list_blocks(layouts, 8)}
                        """
            }


    def code_register(self, context):
        return {
            "code": f"""
                    bpy.utils.register_class(SNA_OT_{self.item.identifier.title()})
                    """
        }


    def code_unregister(self, context):
        return {
            "code": f"""
                    bpy.utils.unregister_class(SNA_OT_{self.item.identifier.title()})
                    """
        }
