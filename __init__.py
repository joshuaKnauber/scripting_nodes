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
    "blender" : (2, 80, 0),
    "version" : (1, 0, 2),
    "location" : "Editors -> Visual Scripting",
    "wiki_url": "", 
    "category" : "Node" 
}

import bpy
import nodeitems_utils
from bpy.app.handlers import persistent
import atexit
import os
import json
import requests
import datetime
from . import auto_load
from bpy.utils import previews
from .node_tree.node_categories import get_node_categories
from .properties.groups.addon_properties import ScriptingNodesProperties
from .properties.groups.package_marketplace import ScriptingNodesMarketplace
from .interface.node_header import node_header
from .interface.right_click_menu import serpens_right_click
from .compile.compiler import compiler
from .operators.keymaps.keymaps import register_keymaps,unregister_keymaps
from .handler.depsgraph import handle_depsgraph_update
from .nodes.execute.run_operator import create_internal_ops

auto_load.init()

@persistent
def unload_collections(dummy=None):
    # clear all collections for nodes that are to big to store or need to be update on reload
    bpy.context.scene.sn_properties.operator_properties.clear()

@persistent
def load_collections(dummy=None):
    # load all collections that are cleared in unload_collections
    create_internal_ops()



def check_for_update():
    url = "https://raw.githubusercontent.com/joshuaKnauber/visual_scripting_addon_docs/packages/packages.json"

    try:
        version = requests.get(url).json()["newest_version"]
        if version[0] > bl_info["version"][0]:
            bpy.ops.scripting_nodes.update_message("INVOKE_DEFAULT",version=tuple(version))
        elif version[0] == bl_info["version"][0]:
            if version[1] > bl_info["version"][1]:
                bpy.ops.scripting_nodes.update_message("INVOKE_DEFAULT",version=tuple(version))
            elif version[1] == bl_info["version"][1]:
                if version[2] > bl_info["version"][2]:
                    bpy.ops.scripting_nodes.update_message("INVOKE_DEFAULT",version=tuple(version))

    except:
        print("Couldn't check for Serpens updates!")

def update_notification():
    prefs = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences

    if prefs.do_update_notif and not prefs.seen_new_update:
        with open(os.path.join(os.path.dirname(__file__),"update_log.json"), "r" ,encoding="utf-8") as update_data:
            update_data = json.loads(update_data.read())
            last_date = datetime.date(year=update_data["last_update"][2],month=update_data["last_update"][1],day=update_data["last_update"][0])
            if (datetime.date.today() - last_date).days >= update_data["update_frequency"]:
                check_for_update()

@persistent
def load_handler(dummy):
    """ function that is run after the file is loaded """
    bpy.context.scene.sn_properties.package_installed_without_compile = False
    bpy.context.scene.sn_properties.package_uninstalled_without_compile = False
    
    bpy.context.scene.sn_properties.show_node_info = False
    bpy.context.scene.sn_properties.show_tutorial = False
    bpy.context.scene.sn_properties.showing_add_to_panel = False
    bpy.context.scene.sn_properties.recording_shortcut = False
    
    compiler().unregister_existing()
    for tree in bpy.data.node_groups:
        if tree.bl_idname == "ScriptingNodesTree":
            if tree.compile_on_start:
                compiler().compile_tree(tree)

    unload_collections()
    load_collections()

    update_notification()

def unload_handler(dummy=None):
    """ function that is run before blender is closed and when a new file is opened """
    compiler().unregister_all()

def reregister_node_categories(names=[]):
    """ reregisters the node categories """
    #TODO: Refresh blender here to reload the nodes
    nodeitems_utils.unregister_node_categories('SCRIPTING_NODES')
    nodeitems_utils.register_node_categories('SCRIPTING_NODES', get_node_categories())

@persistent
def depsgraph_handler(dummy):
    handle_depsgraph_update()

def register_icons():
    bpy.types.Scene.sn_icons = bpy.utils.previews.new()
    icons_dir = os.path.join( os.path.dirname( __file__ ), "icons" )

    icons = [ "discord", "bug", "serpens" ]

    for icon in icons:
        bpy.types.Scene.sn_icons.load( icon, os.path.join( icons_dir, icon + ".png" ), 'IMAGE' )

def unregister_icons():
    bpy.utils.previews.remove( bpy.types.Scene.lp_icons )

def register():
    # register the classes of the addon
    auto_load.register()

    # register the keymaps
    register_keymaps()

    # register the icons
    register_icons()

    # add right click
    try: bpy.types.WM_MT_button_context.append(serpens_right_click)
    except: pass

    # register the node categories
    nodeitems_utils.register_node_categories('SCRIPTING_NODES', get_node_categories())

    # append the node tree header
    bpy.types.NODE_HT_header.append(node_header)

    # add the load handler
    bpy.app.handlers.load_post.append(load_handler)

    # add the save handler
    bpy.app.handlers.save_pre.append(unload_collections)

    # add the save handler
    bpy.app.handlers.save_post.append(load_collections)

    # add the unload handler
    atexit.register(unload_handler)

    # register the depsgraph handler
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_handler)

    # register the addon properties
    bpy.types.Scene.sn_properties = bpy.props.PointerProperty(type=ScriptingNodesProperties)

    # register the marketplace list
    bpy.types.Scene.sn_marketplace = bpy.props.CollectionProperty(type=ScriptingNodesMarketplace)

    # register the addon list
    bpy.types.Scene.sn_addons = bpy.props.CollectionProperty(type=ScriptingNodesMarketplace)

    # register property for storing if the text is a sn file
    bpy.types.Text.is_sn_addon = bpy.props.BoolProperty(default=False)

def unregister():

    # unregister keymaps
    unregister_keymaps()

    # unregister the icons
    unregister_icons()

    # remove right click
    try: bpy.types.WM_MT_button_context.remove(serpens_right_click)
    except: pass

    # unregister the node categories
    nodeitems_utils.unregister_node_categories('SCRIPTING_NODES')

    # remove the function from the node tree header
    bpy.types.NODE_HT_header.remove(node_header)

    # remove the load handler
    bpy.app.handlers.load_post.remove(load_handler)

    # remove the unload handler
    atexit.unregister(unload_handler)

    # unnregister the depsgraph handler
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_handler)

    # unnregister the depsgraph handler
    bpy.app.handlers.save_pre.remove(unload_collections)

    # unnregister the depsgraph handler
    bpy.app.handlers.save_post.remove(load_collections)

    # remove the addon properties
    del bpy.types.Scene.sn_properties

    # remove the marketplace list
    del bpy.types.Scene.sn_marketplace

    # remove the marketplace list
    del bpy.types.Scene.sn_addons

    # unregister property for storing if the text is a sn file
    del bpy.types.Text.is_sn_addon

    # unregister the addon classes
    auto_load.unregister()
