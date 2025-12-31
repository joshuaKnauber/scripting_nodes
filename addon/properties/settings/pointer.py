import bpy
from .settings import PropertySettings, id_items
from ....utils import collection_has_item, collection_get_item


class SN_PT_PointerProperty(PropertySettings, bpy.types.PropertyGroup):

    type_description = (
        "Pointer properties can point to specific types of blend data or property groups.\n"
        + "\n"
        + "They are often used to point to your addons settings, which could live grouped\n"
        + "in a property group and be attached to the scene.\n"
        + "\n"
        + "When used with blend data, you can use pointers to let the user select the data\n"
        + "from a dropdown and get the blend data from the property."
    )

    copy_attributes = ["data_type", "use_prop_group", "prop_group"]

    def draw(self, context, layout):
        """Draws the settings for this property type"""
        src = context.scene.sn
        layout.prop(self, "use_prop_group")
        if not self.use_prop_group:
            layout.prop(self, "data_type")
        else:
            layout.prop_search(
                self, "prop_group", src, "properties", item_search_property="name"
            )
            row = layout.row()
            row.alert = True
            prop_group = collection_get_item(src.properties, self.prop_group) if self.prop_group else None
            if prop_group:
                if not prop_group.property_type == "Group":
                    row.label(
                        text="The selected property is not a group!", icon="ERROR"
                    )
                elif (
                    hasattr(self.prop, "group_prop_parent")
                    and self.prop.group_prop_parent.name == self.prop_group
                ):
                    row.label(
                        text="Can't use self reference for this collection!",
                        icon="ERROR",
                    )
            else:
                row.label(
                    text="There is no valid property group selected!", icon="ERROR"
                )

    @property
    def prop_type_name(self):
        return "PointerProperty"

    @property
    def register_options(self):
        if not self.use_prop_group:
            data_type = "bpy.types." + self.data_type
        else:
            src = self.prop.prop_collection_origin
            data_type = "bpy.types.Scene"
            prop_group = collection_get_item(src.properties, self.prop_group)
            if prop_group and prop_group.property_type == "Group":
                if not hasattr(self.prop, "group_prop_parent") or (
                    hasattr(self.prop, "group_prop_parent")
                    and self.prop.group_prop_parent.name != self.prop_group
                ):
                    scene_prop_group = collection_get_item(bpy.context.scene.sn.properties, self.prop_group)
                    if scene_prop_group:
                        data_type = f"SNA_GROUP_{scene_prop_group.python_name}"
        return f"type={data_type}{self.update_option}"

    def get_data_items(self, context):
        items = []
        for item in id_items:
            items.append((item, item, item))
        return items

    data_type: bpy.props.EnumProperty(
        name="Data Type",
        description="The type of blend data to have this property point to",
        items=get_data_items,
        update=PropertySettings.compile,
    )

    use_prop_group: bpy.props.BoolProperty(
        name="Use Property Group",
        description="Point to a custom property group you created",
        update=PropertySettings.compile,
    )

    prop_group: bpy.props.StringProperty(
        name="Property Group",
        description="The property group you want to point to",
        update=PropertySettings.compile,
    )
