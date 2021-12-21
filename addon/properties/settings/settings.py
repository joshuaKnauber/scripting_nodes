import bpy



class PropertySettings:
    
    @property
    def prop(self):
        for prop in bpy.context.scene.sn.properties:
            if prop.settings == self:
                return prop

    def compile(self, context=None):
        """ Compile the property for these settings """
        self.prop.compile()