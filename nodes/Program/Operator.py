import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyNode import PropertyNode
from ...utils import get_python_name, unique_collection_name



class SN_OperatorNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyNode):

    bl_idname = "SN_OperatorNode"
    bl_label = "Operator"
    def layout_type(self, _): return "layout"
    is_trigger = True
    bl_width_default = 200
    node_color = "PROGRAM"

    def on_node_property_change(self, property):
        self.trigger_ref_update({ "property_change": property })

    def on_node_property_add(self, property):
        property.allow_pointers = False
        self.trigger_ref_update({ "property_add": property })

    def on_node_property_remove(self, index):
        self.trigger_ref_update({ "property_remove": index })

    def on_node_property_move(self, from_index, to_index):
        self.trigger_ref_update({ "property_move": (from_index, to_index) })

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
        # width input
        if self.invoke_option in ["invoke_props_dialog", "invoke_popup"]:
            if len(self.inputs) == 1: self.add_integer_input("Width").default_value = 300
        else:
            if "Width" in self.inputs: self.inputs.remove(self.inputs["Width"])

        # interface output
        if self.invoke_option in ["invoke_props_dialog", "invoke_props_popup"]:
            if not "Popup" in self.outputs:
                self.add_dynamic_interface_output("Popup")
        else:
            if "Popup" in self.outputs:
                for i in range(len(self.outputs)-1, -1, -1):
                    if self.outputs[i].name == "Popup":
                        self.outputs.remove(self.outputs[i])
                
        # filepath outputs
        if self.invoke_option == "IMPORT" or self.invoke_option == "EXPORT":
            if not "Filepath" in self.outputs:
                self.add_string_output("Filepath")
                self.add_list_output("Filepaths")
            if self.invoke_option == "IMPORT":
                self.outputs["Filepaths"].set_hide(not self.allow_multiselect)
            else:
                self.outputs["Filepaths"].set_hide(True)
        else:
            if "Filepath" in self.outputs:
                self.outputs.remove(self.outputs["Filepath"])
                self.outputs.remove(self.outputs["Filepaths"])

        self._evaluate(context)

    operator_description: bpy.props.StringProperty(name="Description", description="Description of the operator", update=update_description)
    invoke_option: bpy.props.EnumProperty(name="Popup",items=[("none","None","None"),
                                                            ("invoke_confirm","Confirm","Shows a confirmation option for this operator"),
                                                            ("invoke_props_dialog","Popup","Opens a customizable property dialog"),
                                                            ("invoke_props_popup", "Property Update", "Show a customizable dialog and execute the operator on property changes"),
                                                            ("invoke_search_popup", "Search Popup", "Opens a search menu from a selected enum property"),
                                                            ("IMPORT", "Import File Browser", "Opens a filebrowser to select items"),
                                                            ("EXPORT", "Export File Browser", "Opens a filebrowser to a location"),
                                                            ("invoke_popup", "Show Properties", "Shows a popup with the operators properties")],update=update_popup)


    select_property: bpy.props.StringProperty(name="Preselected Property",description="The property that is preselected when the popup is opened. This can only be a String or Enum Property!", update=SN_ScriptingBaseNode._evaluate)


    def update_multiselect(self, context):
        self.outputs["Filepaths"].set_hide(not self.allow_multiselect)
        self._evaluate(context)

    allow_multiselect: bpy.props.BoolProperty(default=False, name="Multiselect",
                                        description="Return multiple selected items",
                                        update=update_multiselect)

    extensions: bpy.props.StringProperty(default=".png,.jpg,.exr", name="File Extensions",
                                        description="Allowed file extensions (separated by comma, empty means all are allowed)",
                                        update=SN_ScriptingBaseNode._evaluate)

    export_extension: bpy.props.StringProperty(default=".png", name="Export Extension",
                                        description="Extension that the file is exported with",
                                        update=SN_ScriptingBaseNode._evaluate)
    

    hide_properties: bpy.props.BoolProperty(default=False, name="Hide Properties",
                                        description="Hide the properties section of this operator")


    @property
    def operator_python_name(self):
        return get_python_name(self.name, replacement="my_generic_operator") + f"_{self.static_uid.lower()}"

    def on_create(self, context):
        self.add_boolean_input("Disable")
        self.add_execute_output("Execute")
        self.add_execute_output("Before Popup")


    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "name")
        python_name = get_python_name(self.name, replacement="my_generic_operator")
        row.operator("sn.find_referencing_nodes", text="", icon="VIEWZOOM").node = self.name
        row.operator("sn.copy_python_name", text="", icon="COPYDOWN").name = "sna." + python_name

        layout.label(text="Description: ")
        layout.prop(self, "operator_description", text="")

        layout.prop(self, "invoke_option")

        if self.invoke_option == "IMPORT" or self.invoke_option == "EXPORT":
            layout.prop(self, "extensions")
            if self.invoke_option == "IMPORT":
                layout.prop(self, "allow_multiselect")
            elif self.invoke_option == "EXPORT":
                layout.prop(self, "export_extension")
        elif self.invoke_option == "invoke_search_popup":
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

        if not self.hide_properties:
            self.draw_list(layout)
            
    def draw_node_panel(self, context, layout):
        layout.prop(self, "hide_properties")


    def evaluate(self, context):
        props_imperative_list = self.props_imperative(context).split("\n")
        props_code_list = self.props_code(context).split("\n")
        props_register_list = self.props_register(context).split("\n")
        props_unregister_list = self.props_unregister(context).split("\n")
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
            if not self.invoke_option in ["none", "IMPORT", "EXPORT"]:
                invoke_inline = "context.window_manager." + self.invoke_option + "(self, event)"

        draw_function = ""
        if self.invoke_option in ["invoke_props_dialog","invoke_props_popup"]:
            draw_function = f"""

                        def draw(self, context):
                            layout = self.layout
                            {self.indent([out.python_value for out in self.outputs[2:-1]], 7)}"""
        
        helpers = ""
        extensions = ""
        exp_ext = ""
        files = ""
        if self.invoke_option == "IMPORT" or self.invoke_option == "EXPORT":
            helpers = ", ImportHelper" if self.invoke_option == "IMPORT" else ", ExportHelper"
            if self.extensions:
                extensions = f"filter_glob: bpy.props.StringProperty( default='{self.extensions.replace('.', '*.').replace(',', ';')}', options={{'HIDDEN'}} )"
            if self.invoke_option == "EXPORT":
                if self.export_extension:
                    exp_ext = f"filename_ext = '{self.export_extension}'"
            elif self.invoke_option == "IMPORT" and self.allow_multiselect:
                files = "files: bpy.props.CollectionProperty(name='Filepaths', type=bpy.types.OperatorFileListElement)"
                    
            self.outputs["Filepath"].python_value = "self.filepath"
            if self.invoke_option == "IMPORT" and self.allow_multiselect:
                self.outputs["Filepaths"].python_value = "[os.path.join(os.path.dirname(self.filepath), f.name) for f in self.files]"

        code = f"""
                    {self.indent(props_imperative_list, 5)}
        
                    class SNA_OT_{self.operator_python_name.title()}(bpy.types.Operator{helpers}):
                        bl_idname = "sna.{self.operator_python_name}"
                        bl_label = "{self.name}"
                        bl_description = "{self.operator_description}"
                        bl_options = {"{" + '"REGISTER", "UNDO"' + "}"}
                        {extensions}
                        {exp_ext}
                        {files}
                        {selected_property}
                        {self.indent(props_code_list, 6)}

                        @classmethod
                        def poll(cls, context):
                            return not {self.inputs[0].python_value}

                        def execute(self, context):
                            {self.indent(self.outputs[0].python_value, 7)}
                            return {{"FINISHED"}}

                        {draw_function}
                    """
        invoke =    f"""
                        def invoke(self, context, event):
                            {self.indent(self.outputs[1].python_value, 7)}
                            {invoke_inline}
                            return {invoke_return}
                    """
        
        if not self.invoke_option in ["IMPORT", "EXPORT"]:
            code += invoke
        self.code = code

        self.code_register = f"""
                            {self.indent(props_register_list, 7)}
                            bpy.utils.register_class(SNA_OT_{self.operator_python_name.title()})
                            """
        self.code_unregister = f"""
                            {self.indent(props_unregister_list, 7)}
                            bpy.utils.unregister_class(SNA_OT_{self.operator_python_name.title()})
                            """
                            
        if self.invoke_option == "IMPORT" or self.invoke_option == "EXPORT":
            self.code_import = """
                import os
                from bpy_extras.io_utils import ImportHelper, ExportHelper
                """