import bpy


class SN_OT_CopyOperator(bpy.types.Operator):
    bl_idname = "scripting_nodes.copy_operator"
    bl_label = "Copy Operator"
    bl_description = "Copies this operator for a run operator node"
    bl_options = {"REGISTER","INTERNAL"}

    idname: bpy.props.StringProperty()

    def execute(self, context):
        bpy.context.window_manager.clipboard = self.idname
        return {"FINISHED"}



class SN_OT_PasteOperator(bpy.types.Operator):
    bl_idname = "scripting_nodes.paste_operator"
    bl_label = "Paste Operator"
    bl_description = "Pastes a copied operator for this node"
    bl_options = {"REGISTER","INTERNAL"}

    node_name: bpy.props.StringProperty()

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node_name]

        copied = bpy.context.window_manager.clipboard
        for cat in dir(bpy.ops):
            for op in dir(eval("bpy.ops."+cat)):
                op = eval("bpy.ops." + cat + "." + op)

                if op.idname() == copied:

                    for item in context.scene.sn_properties.operator_properties:
                        if item.identifier == op.idname_py():

                            node.search_prop = "internal"
                            node.propName = item.name
                            print(item.name)
                            self.report({"INFO"},message="Selected copied operator!")
                            return {"FINISHED"}

        self.report({"WARNING"},message="Couldn't find copied operator!")
        return {"FINISHED"}



class WM_MT_button_context(bpy.types.Menu):
    bl_label = "Unused"

    def draw(self, context):
        pass


def serpens_right_click(self, context):
    layout = self.layout

    property_value = getattr(context, "button_prop", None)
    button_value = getattr(context, "button_operator", None)
    
    if button_value:
        layout.separator()
        layout.operator("scripting_nodes.copy_operator",text="Copy for Run Operator",icon_value=bpy.context.scene.sn_icons[ "serpens" ].icon_id).idname = button_value.bl_rna.identifier
