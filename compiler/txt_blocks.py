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
            def exec_line(line):
                exec(line)

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
                if type(value) == tuple:
                    for data in value:
                        if bool(data):
                            return True
                    return False

                return bool(value)

            def sn_cast_float(value):
                if type(value) == str:
                    try:
                        value = float(value)
                        return value
                    except:
                        return float(bool(value))
                elif type(value) == tuple:
                    return float(value[0])
                elif type(value) == list:
                    return float(len(value))
                elif not type(value) in [float, int, bool]:
                    try:
                        value = len(value)
                        return float(value)
                    except:
                        return float(bool(value))
                return float(value)

            def sn_cast_int(value):
                return int(sn_cast_float(value))

            def sn_cast_boolean_vector(value, size):
                if type(value) in [str, bool, int, float]:
                    return_value = []
                    for i in range(size):
                        return_value.append(bool(value))
                    return tuple(return_value)
                elif type(value) == tuple:
                    return_value = []
                    for i in range(size):
                        return_value.append(bool(value[i]) if len(value) > i else bool(value[0]))
                    return tuple(return_value)
                elif type(value) == list:
                    return sn_cast_boolean_vector(tuple(value), size)
                else:
                    try:
                        value = tuple(value)
                        return sn_cast_boolean_vector(value, size)
                    except:
                        return sn_cast_boolean_vector(bool(value), size)

            def sn_cast_float_vector(value, size):
                if type(value) in [str, bool, int, float]:
                    return_value = []
                    for i in range(size):
                        return_value.append(sn_cast_float(value))
                    return tuple(return_value)
                elif type(value) == tuple:
                    return_value = []
                    for i in range(size):
                        return_value.append(sn_cast_float(value[i]) if len(value) > i else sn_cast_float(value[0]))
                    return tuple(return_value)
                elif type(value) == list:
                    return sn_cast_float_vector(tuple(value), size)
                else:
                    try:
                        value = tuple(value)
                        return sn_cast_float_vector(value, size)
                    except:
                        return sn_cast_float_vector(sn_cast_float(value), size)

            def sn_cast_int_vector(value, size):
                return tuple(map(int, sn_cast_float_vector(value, size)))

            def sn_cast_color(value, use_alpha):
                length = 4 if use_alpha else 3
                value = sn_cast_float_vector(value, length)
                tuple_list = []
                for data in range(length):
                    data = value[data] if len(value) > data else value[0]
                    tuple_list.append(sn_cast_float(min(1, max(0, data))))
                return tuple(tuple_list)

            def sn_cast_list(value):
                if type(value) in [str, tuple, list]:
                    return list(value)
                elif type(value) in [int, float, bool]:
                    return [value]
                else:
                    try:
                        value = list(value)
                        return value
                    except:
                        return [value]

            def sn_cast_blend_data(value):
                if type(value) in [tuple, bool, int, float, list]:
                    return None
                elif type(value) == str:
                    try:
                        value = eval(value)
                        return value
                    except:
                        return None
                else:
                    return None

            def sn_cast_enum(string, enum_values):
                for item in enum_values:
                    if item[1] == string:
                        return item[0]
                    elif item[0] == string.upper():
                        return item[0]
                return string

            """