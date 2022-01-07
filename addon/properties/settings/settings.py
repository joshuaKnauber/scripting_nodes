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
        for prop in bpy.context.scene.sn.properties:
            if prop.settings == self:
                return prop

    def compile(self, context=None):
        """ Compile the property for these settings """
        self.prop.compile()