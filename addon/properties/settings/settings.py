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
    
    dummy: bpy.props.StringProperty(name="DUMMY", description="Dummy prop for resolving path")
    
    @property
    def prop(self):
        """ Returns the property these settings belong to """
        # TODO this might not work with nodes
        path = ".".join(repr(self.path_resolve("dummy", False)).split(".")[:-2])
        prop = eval(path)
        return prop

    def compile(self, context=None):
        """ Compile the property for these settings """
        self.prop.compile()