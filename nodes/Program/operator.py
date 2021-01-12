import bpy
import json
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
        draw_property(context, variable, self.layout, self.node_name, "operator_properties", node.property_index)


class SN_OT_GetSetOperatorProperty(bpy.types.Operator):
    bl_idname = "sn.get_set_operator_property"
    bl_label = "Get or Set Operator Property"
    bl_description = "Get or set a property from this operator"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_name: bpy.props.StringProperty()
    getset_type: bpy.props.EnumProperty(items=[("GETTER","Getter","Property getter"),
                                                ("INTERFACE","Interface","Interface property"),
                                                ("SETTER","Setter","Property setter")],
                                        options={"SKIP_SAVE"},
                                        name="Getter/Setter",
                                        description="Add a getter/setter for your property")


    def add_node(self,tree):
        nodes = {"GETTER":"SN_GetPropertyNode",
                 "INTERFACE":"SN_DisplayPropertyNode",
                 "SETTER":"SN_SetPropertyNode"}
        return tree.nodes.new(nodes[self.getset_type])


    def execute(self, context):
        tree = context.space_data.node_tree
        node = tree.nodes[self.node_name]
        prop = node.operator_properties[node.property_index]
        data = {
            "data_block": {
                "type": "Operator",
                "name": "Operator Properties",
                "identifier": "self"
            },
            "full_path": "",
            "identifier": prop.identifier,
            "name": prop.name,
            "type": prop.var_type
        }
        new_node = self.add_node(tree)
        new_node.copied_path = json.dumps(data)
        new_node.location = (node.location[0]+300,node.location[1]-200)
        return {"FINISHED"}

    def draw(self,context):
        self.layout.prop(self,"getset_type",expand=True)
    
    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self)


class SN_OperatorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_OperatorNode"
    bl_label = "Operator"
    # bl_icon = "GRAPH"
    bl_width_default = 250

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
        self.auto_compile(context)

    def update_description(self, context):
        self["operator_description"] = self.operator_description.replace("\"", "'")
        self.item.description = self.operator_description.replace("\"", "'")

    def update_popup(self,context):
        # width input
        if self.invoke_option in ["none", "invoke_confirm","invoke_props_popup","invoke_search_popup"]:
            if len(self.inputs) > 1: self.inputs.remove(self.inputs[1])
        else:
            if len(self.inputs) == 1: self.add_integer_input("Width").set_default(300)
        
        # execute output
        if self.invoke_option in ["invoke_popup"]:
            if "Operator" in self.outputs: self.outputs.remove(self.outputs["Operator"])
        
        else:
            if not "Operator" in self.outputs:
                self.add_execute_output("Operator")
                self.outputs.move(len(self.outputs)-1,1)
        
        # interface output
        if self.invoke_option in ["none","invoke_confirm","invoke_popup","invoke_search_popup"]:
            for i in range(len(self.outputs)-1,-1,-1):
                if self.outputs[i].socket_type == "INTERFACE":
                    self.outputs.remove(self.outputs[i])
        
        else:
            if not "Popup" in self.outputs:
                self.add_dynamic_interface_output("Popup")


    operator_name: bpy.props.StringProperty(name="Name", description="Name of the operator", update=update_name)
    operator_description: bpy.props.StringProperty(name="Description", description="Description of the operator", update=update_description)
    invoke_option: bpy.props.EnumProperty(name="Popup",items=[("none","None","None"),
                                                            ("invoke_confirm","Confirm","Shows a confirmation option for this operator"),
                                                            ("invoke_props_dialog","Popup","Opens a customizable property dialog"),
                                                            ("invoke_popup", "Show Properties", "Shows a popup with the operators properties"),
                                                            ("invoke_props_popup", "Property Update", "Show a customizable dialog and execute the operator on property changes"),
                                                            ("invoke_search_popup", "Search Popup", "Opens a search menu from a selected enum property")],update=update_popup)
    operator_properties: bpy.props.CollectionProperty(type=SN_Variable)
    property_index: bpy.props.IntProperty()
    
    
    select_property: bpy.props.StringProperty(name="Preselected Property",description="The property that is preselected when the popup is opened. This can only be a String or Enum Property!")


    def on_create(self,context):
        self.add_execute_output("Invoke")
        self.add_execute_output("Operator")
        out = self.add_blend_data_output("Operator Properties")
        out.data_type = "Operator"
        out.data_identifier = "self"
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
        col.operator("sn.get_set_operator_property", text="", icon="FORWARD").node_name = self.name
        
        if self.invoke_option == "invoke_search_popup":
            layout.prop_search(self,"select_property",self,"operator_properties",text="Search")
        elif self.invoke_option != "none" and self.invoke_option != "invoke_confirm":
            layout.prop_search(self,"select_property",self,"operator_properties",text="Selected")

#TODO blend data variable
    def what_layout(self, socket):
        return "layout"


    def code_evaluate(self, context, touched_socket):
        property_register = []
        for prop in self.operator_properties:
            property_register.append(prop.property_register())
            
        if touched_socket == self.outputs["Operator Properties"]:
            return {"code":"self"}
        
        execute_code = "pass"
        if "Operator" in self.outputs:
            execute_code = self.outputs["Operator"].code(8)

        invoke_code = self.outputs["Invoke"].code(8)
        inline_invoke = ""
                
        if self.invoke_option in ["invoke_confirm"]:
            return_invoke = "context.window_manager." + self.invoke_option + "(self, event)"
            
        elif self.invoke_option in ["invoke_search_popup"]:
            return_invoke = "self.execute(context)"
            inline_invoke = "context.window_manager." + self.invoke_option + "(self)"
            
        elif self.invoke_option in ["invoke_props_dialog","invoke_popup"]:
            return_invoke = "context.window_manager." + self.invoke_option + f"(self, width={self.inputs[1].code()})"
            
        else:
            return_invoke = "self.execute(context)"
            if not self.invoke_option == "none":
                inline_invoke = "context.window_manager." + self.invoke_option + "(self, event)"
            
        if self.invoke_option in ["none","invoke_confirm","invoke_popup"]:
            draw_function = ""
            
        else:
            layout_code = ""
            if "Popup" in self.outputs:
                layout_code = self.outputs["Popup"].by_name(8)

            draw_function = f"""
                        def draw(self, context):
                            layout = self.layout
                            try:
                                {layout_code if layout_code else "pass"}
                            except Exception as exc:
                                print(str(exc) + " | Error in draw function of {self.operator_name}")
                            """
                            
        selected_property = ""
        if self.select_property and self.select_property in self.operator_properties:
            if self.operator_properties[self.select_property].var_type in ["STRING","ENUM"]:
                selected_property = f"bl_property = \"{self.operator_properties[self.select_property].identifier}\""

        return {
            "code": f"""
                    class SNA_OT_{self.item.identifier.title()}(bpy.types.Operator):
                        bl_idname = "sna.{self.item.identifier}"
                        bl_label = "{self.item.name}"
                        bl_description = "{self.item.description}"
                        bl_options = {"{" + '"REGISTER", "UNDO"' + "}"}
                        {selected_property}

                        {self.list_code(property_register, 6)}

                        @classmethod
                        def poll(cls, context):
                            return {self.inputs[0].code()}

                        def execute(self, context):
                            try:
                                {execute_code if execute_code else "pass"}
                            except Exception as exc:
                                print(str(exc) + " | Error in execute function of {self.operator_name}")

                            return {{"FINISHED"}}

                        def invoke(self, context, event):
                            try:
                                {invoke_code if invoke_code else "pass"}
                                {inline_invoke}
                            except Exception as exc:
                                print(str(exc) + " | Error in invoke function of {self.operator_name}")

                            return {return_invoke}

                        {draw_function}
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
