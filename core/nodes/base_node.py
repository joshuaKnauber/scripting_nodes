import time
from uuid import uuid4

import bpy

from ...core.node_tree.node_tree import ScriptingNodesTree
from ...core.utils.links import handle_link_insert, handle_link_remove
from ...core.utils.sockets import add_socket
from ...interface.overlays.errors.error_drawing import display_error
from ...interface.overlays.nodes.node_drawing import set_node_error, set_node_time
from ...utils import logger
from ...utils.code import normalize_indents


class SN_BaseNode(bpy.types.Node):
    is_sn = True
    bl_label = "Base Node"

    id: bpy.props.StringProperty(default="", name="ID", description="Unique ID of the node")

    def _set_id(self):
        self.id = uuid4().hex[:5].upper()

    @classmethod
    def poll(cls, ntree):
        """ Checks if the node is valid """
        return ntree.bl_idname == ScriptingNodesTree.bl_idname

    def ntree_poll(self, group):
        """ Checks if the node tree is valid """
        return group.bl_idname == ScriptingNodesTree.bl_idname

    @property
    def node_tree(self):
        """Returns the node tree this node lives in"""
        return self.id_data

    def init(self, context: bpy.types.Context):
        """ Called when the node is created """
        self._set_id()
        self.on_create()
        self.compile()

    # Callback for when the node is created
    def on_create(self): return

    def copy(self, node: bpy.types.Node):
        """ Called when the node is copied """
        self._set_id()
        self.on_copy(node)
        self.compile()

    # Callback for when the node is copied
    def on_copy(self, node: bpy.types.Node): return

    def free(self):
        """ Called when the node is deleted """
        self.on_delete()
        self.compile()  # TODO: check if this is necessary

    # Callback for when the node is deleted
    def on_delete(self): return

    def add_input(self, idname: str, name: str = ""):
        """ Adds an input socket to the node """
        return add_socket(self, idname, name, False)

    def add_output(self, idname: str, name: str = ""):
        """ Adds an output socket to the node """
        return add_socket(self, idname, name, True)

    def insert_link(self, link: bpy.types.NodeLink):
        """ Called when a link is inserted """
        handle_link_insert(self, link)

    def remove_link(self, link: bpy.types.NodeLink):
        """ Called when a link is removed """
        handle_link_remove(self, link)

    def update(self):
        """ Called when the node topology changes """
        # handle_link_updates(self) # TODO
        self.compile()  # TEMP

    code: bpy.props.StringProperty(default="", name="Code", description="Generated code for the node")
    code_register: bpy.props.StringProperty(default="", name="Code Register", description="Generated register code for the node")
    code_unregister: bpy.props.StringProperty(default="", name="Code Unregister", description="Generated unregister code for the node")

    def generate(self, context: bpy.types.Context):
        """ Generates the code for the node """

    def compile(self):
        """ Called when the node changes. Forwards the update to the node tree """
        self.generate(bpy.context)
        if self.code_register:  # TODO
            self.node_tree.compile(self)

    def _execute(self, local_vars: dict, global_vars: dict):
        """ Executes the code for the node. Note that this code runs within the context of the running addon """
        t1 = time.time()
        try:
            exec(normalize_indents(self.code), local_vars, global_vars)
            set_node_error(self.id, "")
        except Exception as e:
            logger.log(4, f"Error in node '{self.name}'")  # TODO
            display_error(f"Node '{self.name}': {str(e)}")
            set_node_error(self.id, str(e))
        set_node_time(self.id, (time.time() - t1)*1000)

    def draw_buttons(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        """ Draws the buttons on the node """
        box = layout.box()
        col = box.column(align=True)
        for line in self.code.split("\n"):
            col.label(text=line)
        self.draw_node(context, layout)

    # Callback for when the node is drawn
    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout): return
