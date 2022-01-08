import bpy



id_items = ["Scene", "Action", "Armature", "Brush", "CacheFile", "Camera",
        "Collection", "Curve", "FreestyleLineStyle", "GreasePencil",
        "Image", "Key", "Lattice", "Library", "Light", "LightProbe",
        "Mask", "Material", "Mesh", "MetaBall", "MovieClip", "NodeTree",
        "Object", "PaintCurve", "Palette", "ParticleSettings",
        "Screen", "Sound", "Speaker", "Text", "Texture", "VectorFont",
        "Volume", "WindowManager", "WorkSpace", "World"]



property_icons = {
    "String": "SYNTAX_OFF",
    "Boolean": "FORCE_CHARGE",
    "Float": "CON_TRANSLIKE",
    "Integer": "DRIVER_TRANSFORM",
    "Enum": "PRESET",
    "Pointer": "MONKEY",
    "Collection": "ASSET_MANAGER",
    "Group": "FILEBROWSER",
}



class PropertySettings:
    
    @property
    def prop(self):
        #TODO search correct group here
        for prop in bpy.context.scene.sn.properties:
            if prop.settings == self:
                return prop
            if prop.property_type == "Group":
                for subprop in prop.settings.properties:
                    if subprop.settings == self:
                        return subprop

    def compile(self, context=None):
        """ Compile the property for these settings """
        if self.prop:
            self.prop.compile()