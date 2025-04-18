import bpy


REPLACE_NAMES = {
    "ObjectBase": "bpy.data.objects['Object']",  # outliner object hide
    "LayerCollection": "bpy.context.view_layer.active_layer_collection",  # outliner collection hide
    "SpaceView3D": "bpy.context.screen.areas[0].spaces[0]",  # 3d space data
    "ToolSettings": "bpy.context.scene.tool_settings",  # any space tool settings
}


class SN_OT_CopyProperty(bpy.types.Operator):
    bl_idname = "sn.copy_property"
    bl_label = "Copy Property"
    bl_description = "Copy the path of this property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        # get property details
        property_pointer = getattr(context, "button_pointer", None)
        property_value = getattr(context, "button_prop", None)

        # copy data path if available
        if bpy.ops.ui.copy_data_path_button.poll():
            bpy.ops.ui.copy_data_path_button("INVOKE_DEFAULT", full_path=True)

            context.scene.sn.last_copied_datatype = property_value.type.title()
            path = context.window_manager.clipboard.replace('"', "'")

            if path and path[-1] == "]" and path[:-1].split("[")[-1].isdigit():
                path = "[".join(path.split("[")[:-1])
                context.scene.sn.last_copied_datatype += " Vector"
            elif getattr(property_value, "subtype", None) == "COLOR":
                context.scene.sn.last_copied_datatype += " Vector"

            context.window_manager.clipboard = path
            if property_value.type == "ENUM" and property_value.is_enum_flag:
                context.scene.sn.last_copied_datatype += " Set"

            context.scene.sn.last_copied_datapath = context.window_manager.clipboard

            self.report({"INFO"}, message="Copied!")
            return {"FINISHED"}

        # check if replacement is available
        if property_pointer and property_value:
            if property_pointer.bl_rna.identifier in REPLACE_NAMES:
                context.window_manager.clipboard = f"{REPLACE_NAMES[property_pointer.bl_rna.identifier]}.{property_value.identifier}"
                context.window_manager.clipboard = (
                    context.window_manager.clipboard.replace('"', "'")
                )
                context.scene.sn.last_copied_datatype = property_value.type.title()
                if property_value.type == "ENUM" and property_value.is_enum_flag:
                    context.scene.sn.last_copied_datatype += " Set"
                context.scene.sn.last_copied_datapath = context.window_manager.clipboard
                self.report({"INFO"}, message="Copied!")
                return {"FINISHED"}

        # error when property not available
        self.report(
            {"ERROR"},
            message="We can't copy this property yet! Please use the Blend Data browser to find it!",
        )
        print("Serpens Log: ", property_pointer, property_value)
        return {"CANCELLED"}


class SN_OT_CopyOperator(bpy.types.Operator):
    bl_idname = "sn.copy_operator"
    bl_label = "Copy Operator"
    bl_description = "Copy the path of this operator"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def find_ops_path_from_rna(self, rna_identifier):
        for cat_name in dir(bpy.ops):
            if cat_name[0].isalpha() and not cat_name == "class":
                try:
                    cat = eval(f"bpy.ops.{cat_name}")
                except:
                    cat = None
                if cat:
                    for op_name in dir(cat):
                        if op_name[0].isalpha():
                            try:
                                op = eval(f"bpy.ops.{cat_name}.{op_name}")
                            except:
                                op = None
                            if op and op.get_rna_type().identifier == rna_identifier:
                                return f"bpy.ops.{cat_name}.{op_name}()"
        return None

    def execute(self, context):
        # copy operator if available
        if bpy.ops.ui.copy_python_command_button.poll():
            bpy.ops.ui.copy_python_command_button("INVOKE_DEFAULT")
            self.report({"INFO"}, message="Copied!")
            return {"FINISHED"}

        # get button details
        button_value = getattr(context, "button_operator", None)

        # check if value exists
        if button_value:
            op_path = self.find_ops_path_from_rna(button_value.bl_rna.identifier)
            if op_path:
                context.window_manager.clipboard = op_path
                self.report({"INFO"}, message="Copied!")
                return {"FINISHED"}

        # error when button not available
        self.report(
            {"ERROR"},
            message="We can't copy this operator yet! Please report this to the developers!",
        )
        print("Serpens Log: ", button_value)
        return {"CANCELLED"}


def copy_context():
    context = {}
    for attribute in dir(bpy.context):
        if (
            attribute[0].isalpha()
            and not attribute in ["property"]
            and hasattr(bpy.context, attribute)
            and not callable(getattr(bpy.context, attribute))
        ):
            context[attribute] = getattr(bpy.context, attribute)
    return context


class SN_OT_CopyContext(bpy.types.Operator):
    bl_idname = "sn.copy_context"
    bl_label = "Copy Context"
    bl_description = "Copy the context from this area"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        copied = copy_context()
        context.scene.sn.copied_context.clear()
        context.scene.sn.copied_context.append(copied)
        context.scene.sn.hide_preferences = True
        for screen in bpy.data.screens:
            for area in screen.areas:
                area.tag_redraw()
        self.report({"INFO"}, message="Copied and reloaded!")
        return {"FINISHED"}
