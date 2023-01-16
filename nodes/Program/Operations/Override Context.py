import bpy
from ...base_node import SN_ScriptingBaseNode
from ....settings.data_properties import get_item_type



class SN_OverrideItem(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")
    identifier: bpy.props.StringProperty(name="Identifier", default="")
    type: bpy.props.StringProperty(name="Type", default="")



class SN_OT_AddOverrideInput(bpy.types.Operator):
    bl_idname = "sn.add_override_input"
    bl_label = "Add Override Input"
    bl_description = "Adds an override input"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty(name="Node", default="")

    name: bpy.props.StringProperty(name="Name", default="")
    identifier: bpy.props.StringProperty(name="Identifier", default="")
    type: bpy.props.StringProperty(name="Type", default="")

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        if not self.name in node.inputs:
            inp = node._add_input(node.socket_names[self.type], self.name)
            inp.prev_dynamic = True
            print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
            print(f"Value of {self.name}:")
            print(context.scene.sn.copied_context[0][self.identifier])
            print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
            self.report({"INFO"}, f"Printed the current value of {self.name} in the console")
        return {"FINISHED"}



class SN_OT_AddOverride(bpy.types.Operator):
    bl_idname = "sn.add_override"
    bl_label = "Add Override"
    bl_description = "Opens a popup to add overrides"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty(name="Node", default="")

    overrides: bpy.props.CollectionProperty(type=SN_OverrideItem)
    override: bpy.props.StringProperty(name="Override", default="")

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Add Override")
        if context.scene.sn.copied_context == []:
            row = layout.row()
            row.enabled = False
            row.label(text="Rightclick any option to copy the context in that space")
        else:
            ctxt = f"Copied Context: {context.scene.sn.copied_context[0]['area'].type.replace('_', ' ').title()} {context.scene.sn.copied_context[0]['region'].type.replace('_', ' ').title()}"
            layout.label(text=ctxt)
            layout.prop_search(self, "override", self, "overrides", text="")
            row = layout.row()
            item = None if not self.override in self.overrides.keys() else self.overrides[self.override]
            row.enabled = item != None
            op = row.operator("sn.add_override_input", text="Add", icon="ADD")
            op.node = self.node
            if item != None:
                op.name = item.name
                op.identifier = item.identifier
                op.type = item.type

    def invoke(self, context, event):
        node = context.space_data.node_tree.nodes[self.node]
        self.overrides.clear()

        if context.scene.sn.copied_context != []:
            for key in context.scene.sn.copied_context[0].keys():
                item = self.overrides.add()
                item.name = key.replace("_", " ").title()
                item.identifier = key
                item.type = get_item_type(context.scene.sn.copied_context[0][key])
                if not item.type in node.socket_names:
                    item.type = "Data"
        return context.window_manager.invoke_popup(self, width=300)



class SN_OverrideContextNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_OverrideContextNode"
    bl_label = "Override Context"
    node_color = "PROGRAM"
    bl_width_default = 200

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output("With Override")
        self.add_execute_output("Continue")

    def evaluate(self, context):
        overrides = ""
        override_vars = []
        for inp in self.inputs[1:]:
            identifier = inp.name.lower().replace(' ', '_')
            var_name = f"{identifier}_{self.static_uid}"
            override_vars.append(f"{var_name} = {inp.python_value}")
            overrides += f"{identifier}={var_name}, "
        self.code = f"""
                    {self.indent(override_vars, 5)}
                    with bpy.context.temp_override({overrides}):
                        {self.indent(self.outputs[0].python_value, 6) if self.indent(self.outputs[0].python_value, 6).strip() else "pass"}
                    {self.indent(self.outputs[1].python_value, 5)}
                    """
                    
    def draw_node(self, context, layout):
        row = layout.row()
        row.scale_y = 1.25
        row.operator("sn.add_override", text="Add Override", icon="ADD").node = self.name
