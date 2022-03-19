import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyNode import PropertyNode
from ...utils import get_python_name, unique_collection_name



class SN_OperatorNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyNode):

    bl_idname = "SN_OperatorNode"
    bl_label = "Operator"
    layout_type = "layout"
    is_trigger = True
    bl_width_default = 200
    node_color = "PROGRAM"

    def on_node_property_change(self, property):
        self.trigger_ref_update({ "property_change": property })

    def on_node_property_add(self, property):
        self.trigger_ref_update({ "property_add": property })

    def on_node_property_remove(self, index):
        self.trigger_ref_update({ "property_remove": index })

    def on_node_property_move(self, from_index, to_index):
        self.trigger_ref_update({ "property_move": (from_index, to_index) })

    # operator name change
    # property name change
    # property type change

    def on_node_name_change(self):
        new_name = self.name.replace("\"", "'")
        if not self.name == new_name:
            self.name = new_name
            names = []
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree":
                    for ref in ntree.node_collection("SN_OperatorNode").refs:
                        names.append(ref.node.name)

            new_name = unique_collection_name(self.name, "My Operator", names, " ", includes_name=True)
            if not self.name == new_name:
                self.name = new_name
            self.trigger_ref_update()
            self._evaluate(bpy.context)

    def update_description(self, context):
        self["operator_description"] = self.operator_description.replace("\"", "'")
        self._evaluate(context)

    def update_popup(self, context):
        if self.invoke_option in ["invoke_props_dialog", "invoke_popup"]:
            if len(self.inputs) == 1: self.add_integer_input("Width").default_value = 300
        else:
            if "Width" in self.inputs: self.inputs.remove(self.inputs["Width"])

        if self.invoke_option in ["none","invoke_confirm","invoke_popup","invoke_search_popup"]:
            for out in self.outputs[2:]:
                self.outputs.remove(out)
        else:
            if not "Popup" in self.outputs:
                self.add_dynamic_interface_output("Popup")

        self._evaluate(context)

    operator_description: bpy.props.StringProperty(name="Description", description="Description of the operator", update=update_description)
    invoke_option: bpy.props.EnumProperty(name="Popup",items=[("none","None","None"),
                                                            ("invoke_confirm","Confirm","Shows a confirmation option for this operator"),
                                                            ("invoke_props_dialog","Popup","Opens a customizable property dialog"),
                                                            # ("invoke_popup", "Show Properties", "Shows a popup with the operators properties"),
                                                            ("invoke_props_popup", "Property Update", "Show a customizable dialog and execute the operator on property changes"),
                                                            ("invoke_search_popup", "Search Popup", "Opens a search menu from a selected enum property")],update=update_popup)


    select_property: bpy.props.StringProperty(name="Preselected Property",description="The property that is preselected when the popup is opened. This can only be a String or Enum Property!", update=SN_ScriptingBaseNode._evaluate)


    @property
    def operator_python_name(self):
        return get_python_name(self.name, replacement="my_generic_operator")

    def on_create(self, context):
        self.add_boolean_input("Disable")
        self.add_execute_output("Execute")
        self.add_execute_output("Before Popup")
        self.update_name(context)

    def on_copy(self, old):
        self.update_name(None)


    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "name")
        python_name = get_python_name(self.name, replacement="my_generic_operator")
        row.operator("sn.copy_python_name", text="", icon="COPYDOWN").name = "sna." + python_name

        layout.label(text="Description: ")
        layout.prop(self, "operator_description", text="")
        layout.prop(self, "invoke_option")

        if self.invoke_option == "invoke_search_popup":
            layout.label(text="Search: ")
            layout.prop_search(self,"select_property",self,"properties",text="")
            if self.select_property in self.properties and self.properties[self.select_property].property_type != "Enum":
                row = layout.row()
                row.alert = True
                row.label(text="This property needs to be type Enum!")
        elif not self.invoke_option in ["none", "invoke_confirm"]:
            layout.label(text="Selected: ")
            layout.prop_search(self,"select_property",self,"properties",text="")
            if self.select_property in self.properties and not self.properties[self.select_property].property_type in ["Enum", "String"]:
                row = layout.row()
                row.alert = True
                row.label(text="This property needs to be type Enum or String!")

        self.draw_list(layout)


    def evaluate(self, context):
        props_code = self.props_code(context).split("\n")
        selected_property = ""

        invoke_return = "self.execute(context)"
        invoke_inline = ""

        if not self.invoke_option in ["none", "invoke_confirm"]:
            if self.select_property in self.properties and self.properties[self.select_property].property_type in ["Enum", "String"]:
                selected_property = f"bl_property = '{self.properties[self.select_property].python_name}'"

        if self.invoke_option == "invoke_confirm":
            invoke_return = "context.window_manager." + self.invoke_option + "(self, event)"

        elif self.invoke_option in ["invoke_props_dialog","invoke_popup"]:
            invoke_return = "context.window_manager." + self.invoke_option + f"(self, width={self.inputs[1].python_value})"

        elif self.invoke_option == "invoke_search_popup":
            if self.select_property in self.properties and self.properties[self.select_property].property_type == "Enum":
                selected_property = f"bl_property = '{self.properties[self.select_property].python_name}'"
            invoke_inline = "context.window_manager." + self.invoke_option + "(self)"

        else:
            if not self.invoke_option == "none":
                invoke_inline = "context.window_manager." + self.invoke_option + "(self, event)"

        draw_function = ""
        if self.invoke_option in ["invoke_props_dialog","invoke_props_popup"]:
            draw_function = f"""

                        def draw(self, context):
                            layout = self.layout
                            {self.indent([out.python_value for out in self.outputs[2:-1]], 7)}"""


        self.code = f"""
                    class SNA_OT_{self.operator_python_name.title()}(bpy.types.Operator):
                        bl_idname = "sna.{self.operator_python_name}"
                        bl_label = "{self.name}"
                        bl_description = "{self.operator_description}"
                        bl_options = {"{" + '"REGISTER", "UNDO"' + "}"}
                        {selected_property}
                        {self.indent(props_code, 6)}

                        @classmethod
                        def poll(cls, context):
                            return not {self.inputs[0].python_value}

                        def execute(self, context):
                            {self.indent(self.outputs[0].python_value, 7)}
                            return {{"FINISHED"}}

                        {draw_function}

                        def invoke(self, context, event):
                            {self.indent(self.outputs[1].python_value, 7)}
                            {invoke_inline}
                            return {invoke_return}
                    """

        self.code_register = f"bpy.utils.register_class(SNA_OT_{self.operator_python_name.title()})"
        self.code_unregister = f"bpy.utils.unregister_class(SNA_OT_{self.operator_python_name.title()})"


# TODO
# get_set_node_property ?
# options ?