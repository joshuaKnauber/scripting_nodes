import bpy

def register_dynamic_input(self, socket_idname, socket_name):
    all_sockets = []

    for inp in self.inputs:
        if inp.bl_idname == socket_idname:
            all_sockets.append(inp.is_linked)
        else:
            all_sockets.append(True)

    for i in range(len(all_sockets)):
        if not all_sockets[i]:
            all_sockets[i] = self.inputs[i]
            
    for inp in all_sockets:
        if not inp == True:
            self.inputs.remove(inp)

    self.inputs.new(socket_idname, socket_name)


def get_input_value(self,name,socket_types):
    value = str(self.inputs[name].value)
    errors = []
    if self.inputs[name].is_linked:
        if self.inputs[name].links[0].from_socket.bl_idname in socket_types:
            value = self.inputs[name].links[0].from_socket
        else:
            errors.append("wrong_socket")
    return value, errors

def icon_list():
    return bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys()

def get_types():
    types = []
    for data in dir(bpy.data):
        if eval("type(bpy.data."+data+")") == type(bpy.data.objects):
            try:
                types.append((data, eval("bpy.data."+data+".bl_rna.name.replace('Main ','')"), ""))
            except AttributeError:
                pass

    return types


def get_data_blocks():
    dic = {
        "actions": [["SN_StringSocket", "Name"]],
        "armatures": [["SN_StringSocket", "Name"]],
        "brushes": [["SN_StringSocket", "Name"], ["SN_EnumSocket", "Mode", [('OBJECT', "Object",  ""), ('EDIT', "Edit", ""), ('POSE', "Pose", ""), ('SCULPT', "Sculpt", ""), ('VERTEX_PAINT', "Vertex Paint", ""), ('WEIGHT_PAINT', "Weight Paint", ""), ('TEXTURE_PAINT', "Texture Paint", ""), ('PARTICLE_EDIT', "Particle Edit", ""), ('EDIT_GPENCIL', "Edit Gpencil", ""), ('SCULPT_GPENCIL', "Sculpt Gpencil", ""), ('PAINT_GPENCIL', "Paint Gpencil", ""), ('VERTEX_GPENCIL', "Vertex Gpencil", ""), ('WEIGHT_GPENCIL', "Weight Gpencil", "")]]],
        "cameras": [["SN_StringSocket", "Name"]],
        "collections": [["SN_StringSocket", "Name"]],
        "curves": [["SN_StringSocket", "Name"], ["SN_EnumSocket", "Type", [("CURVE", "Curve", ""), ("SURFACE", "Surface", ""), ("FONT", "Font", "")]]],
        "grease_pencils": [["SN_StringSocket", "Name"]],
        "images": [["SN_StringSocket", "Name"], ["SN_IntSocket", "Width"], ["SN_IntSocket", "Height"], ["SN_BooleanSocket", "Alpha"], ["SN_BooleanSocket", "Float Buffer"], ["SN_BooleanSocket", "Stereo 3D"], ["SN_BooleanSocket", "Is True"], ["SN_BooleanSocket", "Tiled"]],
        "lattices": [["SN_StringSocket", "Name"]],
        "lightprobes": [["SN_StringSocket", "Name"], ["SN_EnumSocket", "Type", [('CUBE', "Cube", ""), ('PLANAR', "Planar", ""), ('GRID', "Grid", "")]]],
        "lights": [["SN_StringSocket", "Name"], ["SN_EnumSocket", "Type", [('POINT', "Point", ""), ('SUN', "Sun", ""), ('SPOT', "Spot", ""), ('AREA', "Area", "")]]],
        "linestyles": [["SN_StringSocket", "Name"]],
        "masks": [["SN_StringSocket", "Name"]],
        "materials": [["SN_StringSocket", "Name"]],
        "meshes": [["SN_StringSocket", "Name"]],
        "metaballs": [["SN_StringSocket", "Name"]],
        "node_groups": [["SN_StringSocket", "Name"], ["SN_EnumSocket", "Type", [('ShaderNodeTree', "Shader", ""), ('CompositorNodeTree', "Compositor", ""), ('TextureNodeTree', "Texture", "")]]],
        "palettes": [["SN_StringSocket", "Name"]],
        "particles": [["SN_StringSocket", "Name"]],
        "scenes": [["SN_StringSocket", "Name"]],
        "speakers": [["SN_StringSocket", "Name"]],
        "texts": [["SN_StringSocket", "Name"]],
        "textures": [["SN_StringSocket", "Name"], ["SN_EnumSocket", "Type", [('NONE', "None", ""), ('BLEND', "Blend", ""), ('CLOUDS', "Clouds", ""), ('DISTORTED_NOISE', "Distorted Noise", ""), ('IMAGE', "Image", ""), ('MAGIC', "Magic", ""), ('MARBLE', "Marble", ""), ('MUSGRAVE', "Musgrave", ""), ('NOISE', "Noise", ""), ('STUCCI', "Stucci", ""), ('VORONOI', "Voronoi", ""), ('WOOD', "Wood", "")]]],
        "volumes": [["SN_StringSocket", "Name"]],
        "worlds": [["SN_StringSocket", "Name"]]
    }
    return dic