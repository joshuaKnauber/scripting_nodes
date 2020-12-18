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
            def sn_is_dev():
                return not ".py" in os.getcwd()
                
            def sn_icon(name):
                if sn_is_dev():
                    if name in bpy.data.images:
                        return bpy.data.images[name].preview.icon_id
                    return ""
                return bpy.context.scene.{addon_tree.sn_graphs[0].short_hand()}_icons[name].icon_id
            """