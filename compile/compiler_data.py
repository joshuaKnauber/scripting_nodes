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

    def comment_block(self,name):
        return f"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# {name}
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""