import bpy
from .settings import PropertySettings



class SN_PT_IntegerProperty(PropertySettings, bpy.types.PropertyGroup):
    
    def draw(self, context, layout, prop):
        """ Draws the settings for this property type """
        layout.prop(self, "subtype")
        layout.prop(self, "unit")
        row = layout.row()
        row.enabled = not self.is_vector
        row.prop(self, "default")

        layout.separator()
        row = layout.row(heading="Minimum")
        row.prop(self, "use_min", text="")
        sub_row = row.row()
        sub_row.enabled = self.use_min
        sub_row.prop(self, "min")

        row = layout.row(heading="Maximum")
        row.prop(self, "use_max", text="")
        sub_row = row.row()
        sub_row.enabled = self.use_max
        sub_row.prop(self, "max")

        row = layout.row(heading="Soft Minimum")
        row.prop(self, "use_soft_min", text="")
        sub_row = row.row()
        sub_row.enabled = self.use_soft_min
        sub_row.prop(self, "soft_min")

        row = layout.row(heading="Soft Maximum")
        row.prop(self, "use_soft_max", text="")
        sub_row = row.row()
        sub_row.enabled = self.use_soft_max
        sub_row.prop(self, "soft_max")
        
        layout.separator()
        layout.prop(self, "is_vector")
        col = layout.column()
        col.enabled = self.is_vector
        col.prop(self, "size")
        
        row = col.row()
        split = row.split(factor=0.4)
        split.alignment = "RIGHT"
        split.label(text="Default")
        sub_col = split.column(align=True)
        for i in range(self.size):
            sub_col.prop(self, "vector_default", index=i, text="")
        
        
    @property
    def prop_type_name(self):
        if self.is_vector:
            return "IntVectorProperty"
        return "IntProperty"
    
    
    @property
    def register_options(self):
        if self.is_vector:
            options = f"size={self.size}, default={tuple(list(self.vector_default)[:self.size])}"
        else:
            options = f"default={self.default}"
        options += f", subtype='{self.subtype}'"
        options += f", unit='{self.unit}'"
        if self.use_min: options += f", min={self.min}"
        if self.use_soft_min: options += f", soft_min={self.soft_min}"
        if self.use_max: options += f", max={self.max}"
        if self.use_soft_max: options += f", soft_max={self.soft_max}"
        return options
    
    
    default: bpy.props.IntProperty(name="Default",
                                    description="Default value of this property (This may not reset automatically for existing attached items)",
                                    update=PropertySettings.compile)
    
    
    def get_subtype_items(self, context):
        items = [("NONE", "None", "No subtype, just a default float input"),
                ("PIXEL", "Pixel", "Pixel"), # TODO proper descriptions
                ("UNSIGNED", "Unsigned", "Unsigned"),
                ("PERCENTAGE", "Percentage", "Percentage"),
                ("FACTOR", "Factor", "Factor"),
                ("ANGLE", "Angle", "Angle"),
                ("TIME", "Time", "Time"),
                ("DISTANCE", "Distance", "Distance"),
                ("DISTANCE_CAMERA", "Distance Camera", "Distance Camera"),
                ("POWER", "Power", "Power"),
                ("TEMPERATURE", "Temperature", "Temperature")]
        if self.is_vector:
            items = [("NONE", "None", "No subtype, just a default float vector input"),
                ("COLOR", "Color", "Color"),
                ("TRANSLATION", "Translation", "Translation"),
                ("DIRECTION", "Direction", "Direction"),
                ("VELOCITY", "Velocity", "Velocity"),
                ("ACCELERATION", "Acceleration", "Acceleration"),
                ("MATRIX", "Matrix", "Matrix"),
                ("EULER", "Euler", "Euler"),
                ("QUATERNION", "Quaternion", "Quaternion"),
                ("AXISANGLE", "Axisangle", "Axisangle"),
                ("XYZ", "XYZ", "XYZ"),
                ("XYZ_LENGTH", "XYZ Length", "XYZ Length"),
                ("COLOR_GAMMA", "Color Gamma", "Color Gamma"),
                ("COORDINATES", "Coordinates", "Coordinates"),
                ("LAYER", "Layer", "Layer"),
                ("LAYER_MEMBER", "Layer Member", "Layer Member"),]
        return items
        
    subtype: bpy.props.EnumProperty(name="Subtype",
                                    description="The subtype of this property. This changes how the property is displayed",
                                    update=PropertySettings.compile,
                                    items=get_subtype_items)
    
    
    unit: bpy.props.EnumProperty(name="Unit",
                                    description="The unit of this property. This changes how the property is displayed",
                                    update=PropertySettings.compile,
                                    items=[("NONE", "None", "No unit, just a default float input"),
                                            ("LENGTH", "Length", "Length"), # TODO proper descriptions
                                            ("AREA", "Area", "Area"),
                                            ("VOLUME", "Volume", "Volume"),
                                            ("ROTATION", "Rotation", "Rotation"),
                                            ("TIME", "Time", "Time"),
                                            ("VELOCITY", "Velocity", "Velocity"),
                                            ("ACCELERATION", "Acceleration", "Acceleration"),
                                            ("MASS", "Mass", "Mass"),
                                            ("CAMERA", "Camera", "Camera"),
                                            ("POWER", "Power", "Power")])
    
    
    use_min: bpy.props.BoolProperty(name="Minimum",
                                    description="Use a minimum property value",
                                    update=PropertySettings.compile)
    
    min: bpy.props.IntProperty(name="Minimum", default=-0,
                                    description="The minimum value of this property",
                                    update=PropertySettings.compile)
    
    use_max: bpy.props.BoolProperty(name="Maximum",
                                    description="Use a maximum property value",
                                    update=PropertySettings.compile)

    use_soft_min: bpy.props.BoolProperty(name="Soft Minimum",
                                    description="Use a soft minimum property value",
                                    update=PropertySettings.compile)
    
    soft_min: bpy.props.IntProperty(name="Soft Minimum", default=-0,
                                    description="The soft minimum value of this property",
                                    update=PropertySettings.compile)
    
    max: bpy.props.IntProperty(name="Maximum", default=1,
                                    description="The maximum value of this property",
                                    update=PropertySettings.compile)
    
    use_soft_max: bpy.props.BoolProperty(name="Soft Maximum",
                                    description="Use a soft maximum property value",
                                    update=PropertySettings.compile)
    
    soft_max: bpy.props.IntProperty(name="Soft Maximum", default=1,
                                    description="The soft maximum value of this property",
                                    update=PropertySettings.compile)
    
    
    is_vector: bpy.props.BoolProperty(name="Is Vector",
                                    description="If this property is a vector",
                                    update=PropertySettings.compile)
    
    size: bpy.props.IntProperty(name="Vector Size", min=2, max=32, default=3,
                                    description="Length of the vector property",
                                    update=PropertySettings.compile)
    
    vector_default: bpy.props.IntVectorProperty(name="Default",
                                    description="Default value of this property (This may not reset automatically for existing attached items)",
                                    size=32,
                                    update=PropertySettings.compile)