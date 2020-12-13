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
from .interface.header.header import prepend_header, append_header

from .node_tree.graphs.graph_ui_lists import SN_Graph, update_graph_index
from .node_tree.variables.variables_ui_list import SN_Variable
from .node_tree.node_tree import update_create_tree
from .settings.addon_properties import SN_AddonProperties


auto_load.init()


@persistent
def load_handler(dummy):
    pass


def unload_handler(dummy=None):
    pass


@persistent
def depsgraph_handler(dummy):
    update_create_tree()
    

def register():
    # register the classes of the addon
    auto_load.register()

    # register the graph properties
    bpy.types.NodeTree.sn_graphs = bpy.props.CollectionProperty(type=SN_Graph)
    bpy.types.NodeTree.sn_graph_index = bpy.props.IntProperty(default=0, update=update_graph_index)
    bpy.types.NodeTree.sn_variables = bpy.props.CollectionProperty(type=SN_Variable)
    bpy.types.NodeTree.sn_variable_index = bpy.props.IntProperty(default=0)

    # addon properties
    bpy.types.Scene.sn = bpy.props.PointerProperty(type=SN_AddonProperties)

    # register the keymaps
    register_keymaps()

    # register node categories
    nodeitems_utils.register_node_categories('SCRIPTING_NODES', get_node_categories())

    # add the node tree header
    bpy.types.NODE_HT_header.append(append_header)
    bpy.types.NODE_HT_header.prepend(prepend_header)

    # app handlers
    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_handler)


def unregister():
    # unregister the addon classes
    auto_load.unregister()

    # remove the node tree header
    bpy.types.NODE_HT_header.remove(append_header)
    bpy.types.NODE_HT_header.remove(prepend_header)

    # unregister the graph properties
    del bpy.types.NodeTree.sn_graphs
    del bpy.types.NodeTree.sn_graph_index

    # addon properties
    del bpy.types.Scene.sn

    # unregister the keymaps
    unregister_keymaps()

    # unregister node categories
    nodeitems_utils.unregister_node_categories('SCRIPTING_NODES')

    # remove handlers
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_handler)