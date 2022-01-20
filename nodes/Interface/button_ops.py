import bpy



class SN_OT_DummyButtonOperator(bpy.types.Operator):
    bl_idname = "sn.dummy_button_operator"
    bl_label = "Dummy Button"
    bl_description = "This button has no operator associated"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        self.report({"INFO"}, message="No operator associated with this button!")
        return {"FINISHED"}



class SN_OT_PasteOperator(bpy.types.Operator):
    bl_idname = "sn.paste_operator"
    bl_label = "Paste Operator"
    bl_description = "Paste a copied operator into this button"
    bl_options = {"REGISTER", "INTERNAL"}
    
    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        if "bpy.ops." in context.window_manager.clipboard:
            bpy.data.node_groups[self.node_tree].nodes[self.node].pasted_operator = context.window_manager.clipboard
        else:
            self.report({"ERROR"}, message="Not a valid blender operator. Use the Rightclick Menu -> Get Serpens Operator button")
        return {"FINISHED"}
