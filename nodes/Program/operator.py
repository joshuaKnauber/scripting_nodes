import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



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
            self.add_integer_input("Width")
        if self.outputs[0].sn_type != "EXECUTE":
            self.add_execute_output("Invoke")
            self.outputs.move(len(self.outputs)-1, 0)
            self.add_execute_output("Operator")
            self.outputs.move(len(self.outputs)-1, 0)
        if len(self.outputs) < 3:
            self.add_interface_output("Popup")


        if self.invoke_option in ["none", "invoke_confirm"]:
            self.inputs.remove(self.inputs[1])
            for i, out in enumerate(self.outputs):
                if i > 1:
                    self.outputs.remove(out)
        elif self.invoke_option == "invoke_popup":
            self.outputs.remove(self.outputs[0])
            self.outputs.remove(self.outputs[0])
        elif self.invoke_option in ["invoke_props_popup", "invoke_props_dialog"]:
            self.inputs.remove(self.inputs[1])


    operator_name: bpy.props.StringProperty(name="Name", description="Name of the operator", update=update_name)
    operator_description: bpy.props.StringProperty(name="Description", description="Description of the operator", update=update_description)
    invoke_option: bpy.props.EnumProperty(name="Popup",items=[("none","None","None"),("invoke_confirm","Confirm","You need to confirm the operator"),("invoke_props_dialog","Property Dialog","Opens a customizable property dialog"), ("invoke_popup", "Popup", "Shows a customizable popup"), ("invoke_props_popup", "Property Popup", "Show operator properties and execute it automatically on changes"), ("invoke_search_popup", "Search Popup", "Opens a search menu from an enum property")],update=update_popup)


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

    def what_layout(self, socket):
        return "layout"

    def code_imperative(self, context):
        popup_text = ""
        if self.invoke_option == "CONFIRM":
            popup_text ="""
                        def invoke(self, context, event):
                            return context.window_manager.invoke_confirm(self, event)
                        """
        elif self.invoke_option == "PANEL":
            popup_layouts = []
            for out in self.outputs[1:-1]:
                popup_layouts.append(out.block(0))

            popup_text =f"""
                        def invoke(self, context, event):
                            return context.window_manager.invoke_props_dialog(self, width=250)

                        def draw(self, context):
                            layout = self.layout
                            {self.list_blocks(popup_layouts, 7)}
                        """


        return {
            "code": f"""
                    class SNA_OT_{self.item.identifier.title()}(bpy.types.Operator):
                        bl_idname = "sna.{self.item.identifier}"
                        bl_label = "{self.item.name}"
                        bl_description = "{self.item.description}"
                        bl_options = {{"REGISTER"}}

                        @classmethod
                        def poll(cls, context):
                            return {self.inputs[0].value}

                        def execute(self, context):
                            {self.outputs[0].block(7)}
                            return {{"FINISHED"}}
                        {popup_text}
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
