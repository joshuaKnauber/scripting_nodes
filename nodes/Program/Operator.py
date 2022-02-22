import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyNode import PropertyNode
from ...utils import get_python_name, unique_collection_name



class SN_OperatorNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyNode):

    bl_idname = "SN_OperatorNode"
    bl_label = "Operator"
    is_trigger = True
    bl_width_default = 200
    node_color = "PROGRAM"

    def update_name(self, context):
        self["operator_name"] = self.operator_name.replace("\"", "'")
        names = []
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for ref in ntree.node_collection("SN_OperatorNode").refs:
                    names.append(ref.node.operator_name)

        self["operator_name"] = unique_collection_name(self.operator_name, "My Operator", names, " ", includes_name=True)
        self._evaluate(context)

    def update_description(self, context):
        self["operator_description"] = self.operator_description.replace("\"", "'")
        self._evaluate(context)

    def update_popup(self, context):
        # width input
        if self.invoke_option in ["none", "invoke_confirm","invoke_props_popup","invoke_search_popup"]:
            if "Width" in self.inputs: self.inputs.remove(self.inputs["Width"])
        else:
            if len(self.inputs) == 1: self.add_integer_input("Width").default_value = 300

        # interface output
        if self.invoke_option in ["none","invoke_confirm","invoke_popup","invoke_search_popup"]:
            for out in self.outputs[2:]:
                self.outputs.remove(out)
        else:
            if not "Popup" in self.outputs:
                self.add_dynamic_interface_output("Popup")

        self._evaluate(context)

    operator_name: bpy.props.StringProperty(default="My Operator", name="Name", description="Name of the operator", update=update_name)
    operator_description: bpy.props.StringProperty(name="Description", description="Description of the operator", update=update_description)
    invoke_option: bpy.props.EnumProperty(name="Popup",items=[("none","None","None"),
                                                            ("invoke_confirm","Confirm","Shows a confirmation option for this operator"),
                                                            ("invoke_props_dialog","Popup","Opens a customizable property dialog"),
                                                            # ("invoke_popup", "Show Properties", "Shows a popup with the operators properties"),
                                                            ("invoke_props_popup", "Property Update", "Show a customizable dialog and execute the operator on property changes"),
                                                            ("invoke_search_popup", "Search Popup", "Opens a search menu from a selected enum property")],update=update_popup)


    select_property: bpy.props.StringProperty(name="Preselected Property",description="The property that is preselected when the popup is opened. This can only be a String or Enum Property!", update=SN_ScriptingBaseNode._evaluate)


    def on_create(self, context):
        self.add_boolean_input("Disable")
        self.add_execute_output("Execute")
        self.add_execute_output("Before Popup")
        self.update_name(context)

    def on_copy(self, old):
        self.update_name(None)


    def draw_node(self, context, layout):
        layout.prop(self, "operator_name")
        layout.label(text="Description: ")
        layout.prop(self, "operator_description", text="")
        layout.prop(self, "invoke_option")

        # if self.invoke_option == "invoke_search_popup":
        #     layout.label(text="Search: ")
        #     layout.prop_search(self,"select_property",self,"properties",text="")
        # elif not self.invoke_option in ["none", "invoke_confirm"]:
        layout.label(text="Selected: ")
        layout.prop_search(self,"select_property",self,"properties",text="")

        self.draw_list(layout)


    def evaluate(self, context):
        python_name = get_python_name(self.operator_name, replacement="my_generic_operator")
        selected_property = ""
        props_code = self.props_code(context).split("\n")

        self.code = f"""
                    class SNA_OT_{python_name.title()}(bpy.types.Operator):
                        bl_idname = "sna.{python_name}"
                        bl_label = "{self.operator_name}"
                        bl_description = "{self.operator_description}"
                        bl_options = {"{" + '"REGISTER", "UNDO"' + "}"}
                        {selected_property}
                        {self.indent(props_code, 6)}

                        @classmethod
                        def poll(cls, context):
                            return not {self.inputs[0].python_value}
                        def execute(self, context):
                            try:
                                {self.outputs[0].python_value if self.outputs[0].python_value.strip() else "pass"}
                            except Exception as exc:
                                print(str(exc) + " | Error in execute function of {self.operator_name}")
                            return {{"FINISHED"}}
                        def invoke(self, context, event):
                            try:
                                {self.outputs[1].python_value if self.outputs[1].python_value.strip() else "pass"}
                            except Exception as exc:
                                print(str(exc) + " | Error in invoke function of {self.operator_name}")
                            return {{"FINISHED"}}
                    """

        self.code_register = f"bpy.utils.register_class(SNA_OT_{python_name.title()})"
        self.code_unregister = f"bpy.utils.unregister_class(SNA_OT_{python_name.title()})"


# invoke options
# select property
# get_set_node_property
# python copy buttons
