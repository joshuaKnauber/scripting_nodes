class DataBlockHandler():

    # CALLABLE FUNCTIONS
    # get_data_blocks: returns the list of data blocks
    # generate_sockets: generates the sockets for the given node

    def get_data_blocks(self):
        dic = {
            "actions": [["SN_StringSocket", "Name"]],
            "armatures": [["SN_StringSocket", "Name"]],
            "brushes": [["SN_StringSocket", "Name"], ["SN_EnumSocket", "Mode", [('OBJECT', "Object",  ""), ('EDIT', "Edit", ""), ('POSE', "Pose", ""), ('SCULPT', "Sculpt", ""), ('VERTEX_PAINT', "Vertex Paint", ""), ('WEIGHT_PAINT', "Weight Paint", ""), ('TEXTURE_PAINT', "Texture Paint", ""), ('PARTICLE_EDIT', "Particle Edit", ""), ('EDIT_GPENCIL', "Edit Gpencil", ""), ('SCULPT_GPENCIL', "Sculpt Gpencil", ""), ('PAINT_GPENCIL', "Paint Gpencil", ""), ('VERTEX_GPENCIL', "Vertex Gpencil", ""), ('WEIGHT_GPENCIL', "Weight Gpencil", "")]]],
            "cameras": [["SN_StringSocket", "Name"]],
            "collections": [["SN_StringSocket", "Name"]],
            "curves": [["SN_StringSocket", "Name"], ["SN_EnumSocket", "Type", [("CURVE", "Curve", ""), ("SURFACE", "Surface", ""), ("FONT", "Font", "")]]],
            "grease_pencils": [["SN_StringSocket", "Name"]],
            "images": [["SN_StringSocket", "Name"], ["SN_IntSocket", "Width"], ["SN_IntSocket", "Height"], ["SN_BooleanSocket", "Alpha"], ["SN_BooleanSocket", "Float Buffer"], ["SN_BooleanSocket", "Stereo 3D"], ["SN_BooleanSocket", "Is Data"], ["SN_BooleanSocket", "Tiled"]],
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

    def generate_sockets(self, node):
        for inp in node.inputs:
            if inp.bl_idname != "SN_ProgramSocket" and inp.bl_idname != "SN_StringSocket":
                node.inputs.remove(inp)
        data = self.get_data_blocks()[node.propLocation]
        for socket in data:
            if socket[0] != "SN_EnumSocket" and socket[1] != "Name":
                node.inputs.new(socket[0], socket[1])
            elif socket[1] != "Name":
                node.inputs.new(socket[0], socket[1])