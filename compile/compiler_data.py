import bpy

gpl_block = """# This program is free software; you can redistribute it and/or modify
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
"""

def addon_info(tree):
    info = """
    'name' : '{0}',
    'author' : '{1}',
    'description' : '{2}',
    'blender' : {3},
    'version' : {4},
    'location' : '{5}',
    'wiki_url': '{6}',
    'warning' : '{7}',
    'category' : '{8}'""".format(tree.addon_name,
                tree.addon_author,
                tree.addon_description,
                "(" + str(tree.addon_blender[0]) + ", " + str(tree.addon_blender[1]) + ", " + str(tree.addon_blender[2]) + ")",
                "(" + str(tree.addon_version[0]) + ", " + str(tree.addon_version[1]) + ", " + str(tree.addon_version[2]) + ")",
                tree.addon_location,
                tree.addon_wiki,
                tree.addon_warning,
                tree.addon_category)

    info = "bl_info = {" + info + "\n}"
    return info


error_logs = {
    "wrong_socket": {
        "title": "Wrong connection",
        "message": "One of the inputs of this node has an incorrect output connected",
        "fatal": True
    },
    "no_connection": {
        "title": "No connections",
        "message": "One of the program outputs of this node has no connections",
        "fatal": False
    },
}