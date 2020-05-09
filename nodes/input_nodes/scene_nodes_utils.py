import bpy

def add_data_output(self,prop,label):
    if type(prop) == str or type(prop) in [bpy.types.StringProperty,bpy.types.EnumProperty]:
        out = self.outputs.new('SN_StringSocket', label)
    elif type(prop) == bool or type(prop) == bpy.types.BoolProperty:
        out = self.outputs.new('SN_BooleanSocket', label)
    elif type(prop) == tuple:# or type(prop) in [bpy.types.FloatVectorProperty]:
        out = self.outputs.new('SN_VectorSocket', label)
    elif type(prop) in [int,float] or type(prop) in [bpy.types.FloatProperty,bpy.types.IntProperty]:
        out = self.outputs.new('SN_NumberSocket', label)
    else:
        print(type(prop))
        out = self.outputs.new('SN_SceneDataSocket', label)
        out.display_shape = "SQUARE"