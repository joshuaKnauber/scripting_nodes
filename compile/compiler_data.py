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
# You can find the addon under PLACEHOLDER.COM
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #"""

    def keymap_block(self):
        return "addon_keymaps = []"

    def register_block(self):
        return "def register():"

    def unregister_block(self):
        return "def unregister():"
        
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