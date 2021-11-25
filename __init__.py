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
    "docs_url": "", 
    "category" : "Node" 
}


import bpy
import nodeitems_utils
from bpy.app.handlers import persistent
from bpy.utils import previews
import atexit

import os

from .keymaps.keymap import register_keymaps, unregister_keymaps
from .node_tree.node_categories import get_node_categories
from .interface.header.header import prepend_header, append_header
from .interface.menu.rightclick import serpens_right_click
from .interface.menu.snippets import snippet_menu

from .settings.addon_properties import SN_AddonProperties
from .settings.updates import check_serpens_updates

from .compiler.compiler import handle_file_load, handle_file_unload

from . import handlers

from . import auto_load
auto_load.init()


@persistent
def load_handler(dummy):
    handle_file_unload()
    handle_file_load()
    check_serpens_updates(bl_info["version"])


def unload_handler(dummy=None):
    handle_file_unload()
    
    
def register_icons():
    bpy.types.Scene.sn_icons = bpy.utils.previews.new()
    icons_dir = os.path.join( os.path.dirname( __file__ ), "assets", "icons" )

    icons = [ "discord", "bug", "serpens" ]

    for icon in icons:
        bpy.types.Scene.sn_icons.load( icon, os.path.join( icons_dir, icon + ".png" ), 'IMAGE' )
        
        
def unregister_icons():
    bpy.utils.previews.remove( bpy.types.Scene.sn_icons )
    

def register():
    # register the classes of the addon
    auto_load.register()
    
    # register the text properties
    # bpy.types.Text.is_sn_addon = bpy.props.BoolProperty(default=False,name="Is Serpens Addon")

    # addon properties
    # bpy.types.Scene.sn = bpy.props.PointerProperty(type=SN_AddonProperties,name="Serpens Properties")

    # register the keymaps
    # register_keymaps()

    # register the icons
    # register_icons()

    # register node categories
    nodeitems_utils.register_node_categories('SCRIPTING_NODES', get_node_categories())

    # add the node tree header
    # bpy.types.NODE_HT_header.append(append_header)
    # bpy.types.NODE_HT_header.prepend(prepend_header)
    # bpy.types.NODE_MT_editor_menus.append(example_dropdown)

    # add to the node add menu
    # bpy.types.NODE_MT_category_snippets.append(snippet_menu)

    # app handlers
    # bpy.app.handlers.load_post.append(load_handler)
    # bpy.app.handlers.depsgraph_update_post.append(handlers.depsgraph_handler)
    # atexit.register(unload_handler)
    
    # add right click menu
    bpy.types.WM_MT_button_context.append(serpens_right_click)


def unregister():
    # remove the node tree header
    # bpy.types.NODE_HT_header.remove(append_header)
    # bpy.types.NODE_HT_header.remove(prepend_header)
    # bpy.types.NODE_MT_editor_menus.remove(example_dropdown)

    # remove from the node add menu
    # bpy.types.NODE_MT_category_snippets.remove(snippet_menu)

    # unregister the text properties
    # del bpy.types.Text.is_sn_addon

    # addon properties
    # del bpy.types.Scene.sn

    # unregister the keymaps
    # unregister_keymaps()

    # unregister the icons
    # unregister_icons()

    # unregister node categories
    nodeitems_utils.unregister_node_categories('SCRIPTING_NODES')

    # remove handlers
    # bpy.app.handlers.load_post.remove(load_handler)
    # bpy.app.handlers.depsgraph_update_post.remove(handlers.depsgraph_handler)
    # atexit.unregister(unload_handler)
    
    # remove right click menu
    try: bpy.types.WM_MT_button_context.remove(serpens_right_click)
    except: pass

    # unregister the addon classes
    auto_load.unregister()