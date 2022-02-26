import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyNode import PropertyNode
from ...utils import get_python_name, unique_collection_name



class SN_RunOperatorNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyNode):

    bl_idname = "SN_RunOperatorNode"
    bl_label = "Run Operator"
    bl_width_default = 200
    node_color = "PROGRAM"

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()

    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "operator_name")
        python_name = get_python_name(self.operator_name, replacement="my_generic_operator")
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
        python_name = get_python_name(self.operator_name, replacement="my_generic_operator")
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
                            {self.indent(self.outputs[0].python_value, 7)}
                            return {{"FINISHED"}}

                        {draw_function}

                        def invoke(self, context, event):
                            {self.indent(self.outputs[1].python_value, 7)}
                            {invoke_inline}
                            return {invoke_return}
                    """

        self.code_register = f"bpy.utils.register_class(SNA_OT_{python_name.title()})"
        self.code_unregister = f"bpy.utils.unregister_class(SNA_OT_{python_name.title()})"


# get_set_node_property ?
# options ?