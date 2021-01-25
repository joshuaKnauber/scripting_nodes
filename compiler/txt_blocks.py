def license_block():
    return """
# This program is free software; you can redistribute it and/or modify
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# This addon was created with the Serpens - Visual Scripting Addon.
# This code is generated from nodes and is not intended for manual editing.
# You can find out more about Serpens at <https://blendermarket.com/products/serpens>.
"""


def serpens_functions(addon_tree):
    return f"""
            def sn_print(tree_name, *args):
                if tree_name in bpy.data.node_groups:
                    item = bpy.data.node_groups[tree_name].sn_graphs[0].prints.add()
                    for arg in args:
                        item.value += str(arg) + ";;;"

                    for area in bpy.context.screen.areas:
                        area.tag_redraw()
                print(*args)
                    
            def sn_cast_string(value):
                return str(value)
                
            def sn_cast_boolean(value):
                return bool(value)

            def sn_cast_boolean_vector(value, size):
                return value

            def sn_cast_float(value, use_factor):
                return float(value)
                
            def sn_cast_color(value, use_alpha):
                return value
                
            def sn_cast_float_vector(value, size):
                return value
                
            def sn_cast_int(value):
                return int(value)
                
            def sn_cast_int_vector(value, size):
                return value
                
            def sn_cast_blend_data(value):
                return value
                
            def sn_cast_list(value):
                return list(value)
            """