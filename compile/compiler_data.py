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
    "same_name_addon": {
        "title": "Same name",
        "message": "The addons name exists and it was not compiled",
        "fatal": True
    },
    "wrong_socket": {
        "title": "Wrong connection",
        "message": "At least one of the inputs of this node has an incorrect output connected",
        "fatal": True
    },
    "no_connection": {
        "title": "No connections",
        "message": "At least one of the program outputs of this node has no connections",
        "fatal": False
    },
    "no_connection_for": {
        "title": "No Scene Data connection",
        "message": "The for Node has no scene data inputs",
        "fatal": True
    },
    "no_name_panel": {
        "title": "No name",
        "message": "The panel doesn't have a name",
        "fatal": False
    },
    "no_location_panel": {
        "title": "No location",
        "message": "The panel doesn't have a proper location",
        "fatal": True
    },
    "wrong_location_panel": {
        "title": "Wrong location",
        "message": "The panel has a wrong location",
        "fatal": True
    },
    "no_name": {
        "title": "No name",
        "message": "The variable doesn't have a name",
        "fatal": True
    },
    "invalid_prop": {
        "title": "Invalid property",
        "message": "The property does not exist",
        "fatal": False
    },
    "no_available": {
        "title": "No variable available",
        "message": "With your current connections there is no variable available to use",
        "fatal": True
    },
    "no_operator": {
        "title": "No operator available",
        "message": "There is no operator available to use",
        "fatal": True
    },
    "same_name_function": {
        "title": "Same name",
        "message": "Two functions have the same name",
        "fatal": True
    },
    "same_name_panel": {
        "title": "Same name",
        "message": "Two panels have the same name",
        "fatal": True
    },
    "same_name_operator": {
        "title": "Same name",
        "message": "Two operators have the same name",
        "fatal": True
    },
}


import_texts = """import bpy"""


def register_text(indents,unregister, property_nodes, existing_interface):

    interfaceString = ""
    for interface in existing_interface:
        if "bpy.types" in interface:
            interface = interface.split("(")
            if not unregister:
                interfaceString += " "*indents + interface[0] + "append(" + interface[1] + " \n"
            else:
                interfaceString += " "*indents + interface[0] + "remove(" + interface[1] + " \n"

    regPropertyString = ""
    for propertyName in property_nodes:
        regPropertyString+="    " + propertyName + "\n"
    unregPropertyString = ""
    for propertyName in property_nodes:
        propertyName = propertyName.split(" ")
        unregPropertyString+="    del " + propertyName[0] + "\n"

    if not unregister:
        text = "def register():\n"+ regPropertyString + " "*indents + "for cls in classes:\n"+(" "*indents*2)+"if not hasattr(bpy.types,cls.bl_idname):\n"+(" "*indents*3)+"bpy.utils.register_class(cls)\n"
    else:
        text = "def unregister():\n"+unregPropertyString + " "*indents + "for cls in classes:\n"+(" "*indents*2)+"if hasattr(bpy.types,cls.bl_idname):\n"+(" "*indents*3)+"bpy.utils.unregister_class(cls)\n"
        
    text += interfaceString

    return text