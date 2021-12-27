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
 


bl_info = {
    "name" : "Serpens",
    "author" : "Joshua Knauber, Finn Knauber", 
    "description" : "Adds a node editor for building addons with nodes",
    "blender" : (3, 0, 0),
    "version" : (3, 0, 0),
    "location" : "Editors -> Visual Scripting",
    "doc_url": "", 
    "category" : "Node" 
}



import bpy
import nodeitems_utils
from bpy.utils import previews
import atexit

import os

from .keymaps.keymap import register_keymaps, unregister_keymaps
from .node_tree.node_categories import get_node_categories
from .interface.header.header import header_prepend, header_append
from .interface.menus.rightclick import serpens_right_click
from .interface.menus.snippets import snippet_menu

from .settings.addon_properties import SN_AddonProperties

from . import handlers

from . import auto_load
auto_load.init()



def register_icons():
    bpy.types.Scene.sn_icons = bpy.utils.previews.new()
    icons_dir = os.path.join( os.path.dirname( __file__ ), "assets", "icons")

    icons = ["discord", "serpens"]

    for icon in icons:
        bpy.types.Scene.sn_icons.load(icon, os.path.join( icons_dir, icon + ".png" ), 'IMAGE')



def unregister_icons():
    bpy.utils.previews.remove( bpy.types.Scene.sn_icons )



def register():
    # register the classes of the addon
    auto_load.register()

    # addon properties
    bpy.types.Scene.sn = bpy.props.PointerProperty(type=SN_AddonProperties, name="Serpens Properties")

    # register the keymaps
    register_keymaps()

    # register the icons
    register_icons()

    # register node categories
    nodeitems_utils.register_node_categories('SCRIPTING_NODES', get_node_categories())

    # add the node tree header
    bpy.types.NODE_HT_header.append(header_append)
    bpy.types.NODE_MT_editor_menus.append(header_prepend)

    # add to the node add menu
    # bpy.types.NODE_MT_category_snippets.append(snippet_menu)

    # app handlers
    bpy.app.handlers.depsgraph_update_post.append(handlers.depsgraph_handler)
    bpy.app.handlers.load_post.append(handlers.load_handler)
    bpy.app.handlers.load_pre.append(handlers.unload_handler)
    atexit.register(handlers.unload_handler)
    
    # add right click menu
    bpy.types.WM_MT_button_context.append(serpens_right_click)


def unregister():
    # remove the node tree header
    bpy.types.NODE_MT_editor_menus.remove(header_prepend)
    bpy.types.NODE_HT_header.remove(header_append)

    # remove from the node add menu
    # bpy.types.NODE_MT_category_snippets.remove(snippet_menu)

    # addon properties
    del bpy.types.Scene.sn

    # unregister the keymaps
    unregister_keymaps()

    # unregister the icons
    unregister_icons()

    # unregister node categories
    nodeitems_utils.unregister_node_categories('SCRIPTING_NODES')

    # remove handlers
    bpy.app.handlers.depsgraph_update_post.remove(handlers.depsgraph_handler)
    bpy.app.handlers.load_post.remove(handlers.load_handler)
    bpy.app.handlers.load_pre.remove(handlers.unload_handler)
    atexit.unregister(handlers.unload_handler)
    
    # remove right click menu
    if hasattr(bpy.types, "WM_MT_button_context"):
        bpy.types.WM_MT_button_context.remove(serpens_right_click)

    # unregister the addon classes
    auto_load.unregister()