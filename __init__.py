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
    "name" : "Visual Scripting",
    "author" : "Joshua Knauber, Finn Knauber", 
    "description" : "Adds a node editor for writing scripts and addons with nodes",
    "blender" : (2, 80, 0),
    "version" : (1, 0, 0),
    "location" : "Editors -> Scripting Nodes",
    "wiki_url": "", 
    "warning" : "This addon is still in early development",
    "category" : "Node" 
}

import bpy
import nodeitems_utils
from bpy.app.handlers import persistent
import atexit
from . import auto_load
from .nodes.base.node_categories import get_node_categories
from .properties.groups.addon_properties import ScriptingNodesProperties
from .interface.node_header import node_header
from .compile.compiler import compiler

auto_load.init()

@persistent
def load_handler(dummy):
    """ function that is run after the file is loaded """
    compiler().unregister_existing()
    for tree in bpy.data.node_groups:
        if tree.bl_idname == "ScriptingNodesTree":
            if tree.compile_on_start:
                compiler().compile_tree(tree)

def unload_handler(dummy=None):
    """ function that is run before blender is closed and when a new file is opened """
    compiler().unregister_all()

def reregister_node_categories():
    """ reregisters the node categories """
    nodeitems_utils.unregister_node_categories('SCRIPTING_NODES')
    nodeitems_utils.register_node_categories('SCRIPTING_NODES', get_node_categories())

def register():
    # register the classes of the addon
    auto_load.register()
    
    # register the node categories
    nodeitems_utils.register_node_categories('SCRIPTING_NODES', get_node_categories())

    # append the node tree header
    bpy.types.NODE_HT_header.append(node_header)

    # add the load handler
    bpy.app.handlers.load_post.append(load_handler)

    # add the unload handler
    atexit.register(unload_handler)

    # register the addon properties
    bpy.types.Scene.sn_properties = bpy.props.PointerProperty(type=ScriptingNodesProperties)

    # register property for storing if the text is a sn file
    bpy.types.Text.is_sn_addon = bpy.props.BoolProperty(default=False)

def unregister():
    # unregister the addon classes
    auto_load.unregister()

    # unregister the node categories
    nodeitems_utils.unregister_node_categories('SCRIPTING_NODES')

    # remove the function from the node tree header
    bpy.types.NODE_HT_header.remove(node_header)

    # remove the load handler
    bpy.app.handlers.load_post.remove(load_handler)

    # remove the unload handler
    atexit.unregister(unload_handler)

    # remove the addon properties
    del bpy.types.Scene.sn_properties

    # unregister property for storing if the text is a sn file
    del bpy.types.Text.is_sn_addon