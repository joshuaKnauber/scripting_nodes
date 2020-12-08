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
    "version" : (1, 1, 0),
    "location" : "Editors -> Visual Scripting",
    "wiki_url": "", 
    "category" : "Node" 
}


import bpy
import nodeitems_utils
from bpy.app.handlers import persistent

from . import auto_load

from .keymaps.keymap import register_keymaps, unregister_keymaps
from .node_tree.node_categories import get_node_categories


auto_load.init()


@persistent
def load_handler(dummy):
    pass


def unload_handler(dummy=None):
    pass


@persistent
def depsgraph_handler(dummy):
    pass
    

def register():
    # register the classes of the addon
    auto_load.register()

    # register the keymaps
    register_keymaps()

    # register node categories
    nodeitems_utils.register_node_categories('SCRIPTING_NODES', get_node_categories())


def unregister():
    # unregister keymaps
    unregister_keymaps()

    # register node categories
    nodeitems_utils.unregister_node_categories('SCRIPTING_NODES')

    # unregister the addon classes
    auto_load.unregister()