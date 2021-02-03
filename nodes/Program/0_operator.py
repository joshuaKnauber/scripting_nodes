import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup
from ...node_tree.variables.variables_ui_list import SN_Variable
from ...interface.sidepanel.graph_panels import draw_property
from ...interface.menu.rightclick import construct_from_property


class SN_OT_AddNodeProperty(bpy.types.Operator):
    bl_idname = "sn.add_node_property"
    bl_label = "Add Node Property"
    bl_description = "Adds a new property to this node"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_name: bpy.props.StringProperty()

    def execute(self, context):
        addon_tree = context.space_data.node_tree
        node = addon_tree.nodes[self.node_name]

        variable = node.properties.add()
        variable.from_node_uid = node.uid
        variable.from_node_collection = "properties"
        variable.is_property = True
        variable.use_self = True
        variable.node_tree = addon_tree
        variable.name = "New Property"
        node.property_index = len(node.properties)-1
        if hasattr(node,"sync_inputs"):
            node.sync_inputs()

        return {"FINISHED"}


class SN_OT_RemoveNodeProperty(bpy.types.Operator):
    bl_idname = "sn.remove_node_property"
    bl_label = "Remove Node Property"
    bl_description = "Remove a property from this node"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_name: bpy.props.StringProperty()

    def execute(self, context):
        addon_tree = context.space_data.node_tree
        node = addon_tree.nodes[self.node_name]
        
        for graph in node.addon_tree.sn_graphs:
            for graph_node in graph.node_tree.nodes:
                if graph_node.bl_idname in ["SN_GetPropertyNode", "SN_SetPropertyNode", "SN_DisplayPropertyNode", "SN_UpdatePropertyNode"]:
                    graph_node.on_outside_update(construct_from_property("self", node.properties[node.property_index],node.uid, removed=True))

        node.properties.remove(node.property_index)
        if len(node.properties):
            node.property_index = len(node.properties)-1
        if hasattr(node,"sync_inputs"):
            node.sync_inputs()
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class SN_OT_EditNodeProperty(bpy.types.Operator):
    bl_idname = "sn.edit_node_property"
    bl_label = "Edit Node Property"
    bl_description = "Edit a property from this node"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_name: bpy.props.StringProperty()

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=350)

    def draw(self, context):
        addon_tree = context.space_data.node_tree
        node = addon_tree.nodes[self.node_name]
        variable = node.properties[node.property_index]
        draw_property(context, variable, self.layout, self.node_name, "properties", node.property_index)


class SN_OT_GetSetNodeProperty(bpy.types.Operator):
    bl_idname = "sn.get_set_node_property"
    bl_label = "Get or Set Node Property"
    bl_description = "Get or set a property from this node"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def get_items(self, context):
        items = [("GETTER","Getter","Property getter"),("INTERFACE","Interface","Interface property"),("SETTER","Setter","Property setter")]
        node = context.space_data.node_tree.nodes[self.node_name]
        if not node.properties[node.property_index].has_update():
            items.append(("UPDATE", "Update", "Update Function"))
        return items

    node_name: bpy.props.StringProperty()
    getset_type: bpy.props.EnumProperty(items=get_items,
                                        options={"SKIP_SAVE"},
                                        name="Getter/Setter",
                                        description="Add a getter/setter for your property")


    def add_node(self,tree):
        nodes = {"GETTER":"SN_GetPropertyNode",
                 "INTERFACE":"SN_DisplayPropertyNode",
                 "SETTER":"SN_SetPropertyNode",
                 "UPDATE":"SN_UpdatePropertyNode"}
        bpy.ops.node.add_node("INVOKE_DEFAULT",type=nodes[self.getset_type],use_transform=True)
        if self.getset_type == "UPDATE":
            tree.nodes.active.wrong_add = False


    def execute(self, context):
        tree = context.space_data.node_tree
        node = tree.nodes[self.node_name]
        prop = node.properties[node.property_index]
        
        self.add_node(tree)
        tree.nodes.active.copied_path = construct_from_property("self",prop, node.uid)
        return {"FINISHED"}

    def draw(self,context):
        self.layout.prop(self,"getset_type",expand=True)
    
    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self)


class SN_OperatorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_OperatorNode"
    bl_label = "Operator"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "has_collection": True,
        "collection_name_attr": "operator_name"
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
        self.auto_compile()

    def update_description(self, context):
        self["operator_description"] = self.operator_description.replace("\"", "'")
        self.item.description = self.operator_description.replace("\"", "'")
        self.auto_compile()

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

        self.auto_compile()


    operator_name: bpy.props.StringProperty(name="Name", description="Name of the operator", update=update_name)
    operator_description: bpy.props.StringProperty(name="Description", description="Description of the operator", update=update_description)
    invoke_option: bpy.props.EnumProperty(name="Popup",items=[("none","None","None"),
                                                            ("invoke_confirm","Confirm","Shows a confirmation option for this operator"),
                                                            ("invoke_props_dialog","Popup","Opens a customizable property dialog"),
                                                            # ("invoke_popup", "Show Properties", "Shows a popup with the operators properties"),
                                                            ("invoke_props_popup", "Property Update", "Show a customizable dialog and execute the operator on property changes"),
                                                            ("invoke_search_popup", "Search Popup", "Opens a search menu from a selected enum property")],update=update_popup)
    properties: bpy.props.CollectionProperty(type=SN_Variable)
    property_index: bpy.props.IntProperty(name="Operator Property Index")
    
    
    select_property: bpy.props.StringProperty(name="Preselected Property",description="The property that is preselected when the popup is opened. This can only be a String or Enum Property!", update=SN_ScriptingBaseNode.auto_compile)


    def sync_inputs(self,index=-1):
        sync_to = ["SN_RunOperatorNode","SN_ButtonNode","SN_OnKeypressNode"]
        if self.item:
            this_name = self.item.name
            for graph in self.addon_tree.sn_graphs:
                for node in graph.node_tree.nodes:
                    if node.bl_idname in sync_to and node.custom_operator == this_name:
                        node.update_inputs_from_operator(index)
                    
    
    def update_from_collection(self,collection,item):
        for i in range(len(self.properties)):
            if self.properties[i] == item:
                self.sync_inputs(i)
                break


    def on_create(self,context):
        self.add_execute_output("Invoke")
        self.add_execute_output("Operator")
        self.add_boolean_input("Poll")
        self.update_name(None)
        
        
    def on_copy(self,node):
        for prop in node.properties:
            prop.from_node_uid = self.uid

    def on_free(self):
        for prop in self.properties:
            bpy.ops.sn.remove_node_property(node_name=self.name)


    def draw_node(self,context,layout):
        layout.prop(self, "operator_name")
        layout.label(text="Description: ")
        layout.prop(self, "operator_description", text="")
        layout.prop(self, "invoke_option")

        row = layout.row(align=False)
        row.template_list("SN_UL_VariableList", "Properties", self, "properties", self, "property_index",rows=3)
        col = row.column(align=True)
        col.operator("sn.add_node_property", text="", icon="ADD").node_name = self.name
        col = col.column(align=True)
        col.enabled = bool(len(self.properties))
        col.operator("sn.remove_node_property", text="", icon="REMOVE").node_name = self.name
        col.operator("sn.edit_node_property", text="", icon="GREASEPENCIL").node_name = self.name
        col.operator("sn.get_set_node_property", text="", icon="FORWARD").node_name = self.name
        
        if self.invoke_option == "invoke_search_popup":
            layout.prop_search(self,"select_property",self,"properties",text="Search")
        elif self.invoke_option != "none" and self.invoke_option != "invoke_confirm":
            layout.prop_search(self,"select_property",self,"properties",text="Selected")


    def what_layout(self, socket):
        return "layout"


    def code_evaluate(self, context, touched_socket):
        if not self.inputs[0].value and not self.inputs[0].links:
            self.add_error("Poll False", "You poll is false and not connected so your operator will not run", fatal=True)

        property_register = []
        for prop in self.properties:
            property_register.append(prop.property_register())
            
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
                                {layout_code if layout_code.strip() else "pass"}
                            except Exception as exc:
                                print(str(exc) + " | Error in draw function of {self.operator_name}")
                            """
                            
        selected_property = ""
        if self.select_property and self.select_property in self.properties:
            if self.properties[self.select_property].var_type in ["STRING","ENUM"]:
                selected_property = f"bl_property = \"{self.properties[self.select_property].identifier}\""

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
                                {execute_code if execute_code.strip() else "pass"}
                            except Exception as exc:
                                print(str(exc) + " | Error in execute function of {self.operator_name}")

                            return {{"FINISHED"}}

                        def invoke(self, context, event):
                            try:
                                {invoke_code if invoke_code.strip() else "pass"}
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
