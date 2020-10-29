class CompilerData():

    def license_block(self):
        return """# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>."""

    def scripting_nodes_block(self):
        return """# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This addon was generated with the Visual Scripting Addon.
# You can find the addon under https://blendermarket.com/products/serpens
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #"""

    def keymap_block(self):
        return "addon_keymaps = []"

    def register_block(self):
        return "def register():"

    def unregister_block(self):
        return "def unregister():"

    def array_class_block(self):
        return """ # Create Array Collection for use in PROPERTIES
class ArrayCollection_UID_(bpy.types.PropertyGroup):
    string: bpy.props.StringProperty()
    string_filepath: bpy.props.StringProperty(subtype='FILE_PATH')
    string_dirpath: bpy.props.StringProperty(subtype='DIR_PATH')
    bool: bpy.props.BoolProperty()

    int: bpy.props.IntProperty()
    int_pixel: bpy.props.IntProperty(subtype="PIXEL")
    int_unsigned: bpy.props.IntProperty(subtype="UNSIGNED")
    int_percentage: bpy.props.IntProperty(subtype="PERCENTAGE")
    int_factor: bpy.props.IntProperty(subtype="FACTOR")
    int_angle: bpy.props.IntProperty(subtype="ANGLE")
    int_time: bpy.props.IntProperty(subtype="TIME")
    int_distance: bpy.props.IntProperty(subtype="DISTANCE")

    float: bpy.props.FloatProperty()
    float_pixel: bpy.props.FloatProperty(subtype="PIXEL")
    float_unsigned: bpy.props.FloatProperty(subtype="UNSIGNED")
    float_percentage: bpy.props.FloatProperty(subtype="PERCENTAGE")
    float_factor: bpy.props.FloatProperty(subtype="FACTOR")
    float_angle: bpy.props.FloatProperty(subtype="ANGLE")
    float_time: bpy.props.FloatProperty(subtype="TIME")
    float_distance: bpy.props.FloatProperty(subtype="DISTANCE")

    vector: bpy.props.FloatVectorProperty()
    four_vector: bpy.props.FloatVectorProperty(size=4)
    color: bpy.props.FloatVectorProperty(subtype='COLOR')
    four_color: bpy.props.FloatVectorProperty(subtype='COLOR', size=4)
"""

    def functions_block(self):
        return """def sn_print(*text):
    text = ', '.join(map(str, text))
    print(text) # actual print command
    try: # try to find the area in which the addon is opened and add the print text
        for area in bpy.context.screen.areas:
            if area.type == "NODE_EDITOR":
                if area.spaces[0].node_tree:
                    if area.spaces[0].node_tree.bl_idname == "ScriptingNodesTree":
                        if sn_tree_name == area.spaces[0].node_tree.name:
                            bpy.context.scene.sn_properties.print_texts.add().text = str(text)

        for area in bpy.context.screen.areas:
            area.tag_redraw()
    except: pass
    
def get_enum_identifier(enumItems, name):
    for item in enumItems:
        if item.name == name:
            return item.identifier
            
    return ''
    
def get_python_filepath():
    path = os.path.dirname(bpy.data.filepath)
    try:
        __file__
        exported = True
    except:
        exported = False
    if exported:
        path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    return path"""

    def utility_block(self):
        return """def cast_int(cast):
    int_string = ""
    if type(cast) == str:
        for char in cast:
            if char.isnumeric():
                int_string+=char
    else:
        return cast[0]
    if int_string.isnumeric():
        int_string = int(int_string)
        return int_string
    return 0

def cast_float(cast):
    float_string = ""
    if type(cast) == str:
        for char in cast:
            if char.isnumeric() or char == ".":
                float_string+=char
    else:
        return cast[0]
    if float_string != "" and float_string != ".":
        float_string = float(float_string)
        return float_string
    return 0
    
def cast_vector(cast):
    if type(cast) == bool:
        if cast:
            return (1.0, 1.0, 1.0)
        else:
            return (0.0, 0.0, 0.0)
    elif type(cast) == int:
        return (float(cast), float(cast), float(cast))
    elif type(cast) == float:
        return (cast, cast, cast)
    elif type(cast) == str:
        cast = cast_float(cast)
        return (cast, cast, cast)
    return (0, 0, 0)

def cast_four_vector(cast, four):
    if type(cast) == bool:
        if cast:
            return (1.0, 1.0, 1.0, four)
        else:
            return (0.0, 0.0, 0.0, four)
    elif type(cast) == int:
        return (float(cast), float(cast), float(cast), four)
    elif type(cast) == float:
        return (cast, cast, cast, four)
    elif type(cast) == str:
        cast = cast_float(cast)
        return (cast, cast, cast, four)
    return (0, 0, 0)"""

    def comment_block(self,name):
        return f"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# {name}
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""