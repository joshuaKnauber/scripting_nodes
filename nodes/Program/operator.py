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
        "register_order": 0,
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
        if self.popup_option == "PANEL":
            if len(self.outputs) == 1:
                self.add_dynamic_interface_output("Popup")
        else:
            for i, out in enumerate(self.outputs):
                if i:
                    try: self.outputs.remove(out)
                    except: pass

    operator_name: bpy.props.StringProperty(name="Name", description="Name of the operator", update=update_name)
    operator_description: bpy.props.StringProperty(name="Description", description="Description of the operator", update=update_description)
    popup_option: bpy.props.EnumProperty(name="Popup Type",items=[("NONE","None","None"),("CONFIRM","Confirm","Confirm"),("PANEL","Popup","Popup")],update=update_popup)


    def on_create(self,context):
        self.add_execute_output("Operator")
        self.add_boolean_input("Should Run")
        self.update_name(None)


    def draw_node(self,context,layout):
        layout.prop(self, "operator_name")
        layout.label(text="Description: ")
        layout.prop(self, "operator_description", text="")
        layout.prop(self, "popup_option", expand=True)

    def what_layout(self, socket):
        return "layout"

    def code_imperative(self, context):
        popup_text = ""
        if self.popup_option == "CONFIRM":
            popup_text ="""
                        def invoke(self, context, event):
                            return context.window_manager.invoke_confirm(self, event)
                        """
        elif self.popup_option == "PANEL":
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
                        bl_options = {"{"}"REGISTER"{"}"}

                        @classmethod
                        def poll(cls, context):
                            return {self.inputs[0].value}

                        def execute(self, context):
                            {self.outputs[0].block(7)}
                            return {"{"}"FINISHED"{"}"}
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
