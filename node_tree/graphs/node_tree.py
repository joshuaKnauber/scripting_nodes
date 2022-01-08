import bpy
from ..sockets.conversions import CONVERSIONS
from .node_refs import NodeRefCollection



def compile_all(hard=False):
    """ Compile all node trees in this file """
    for prop in bpy.context.scene.sn.properties:
        prop.prop_register()
    for group in bpy.data.node_groups:
        if group.bl_idname == "ScriptingNodesTree":
            group.compile(hard)



def unregister_all():
    """ Unregister all node trees in this file """
    for prop in bpy.context.scene.sn.properties:
        prop.prop_unregister()
    for group in bpy.data.node_groups:
        if group.bl_idname == "ScriptingNodesTree":
            group.graph_unregister()
    for key in bpy.context.scene.sn.unregister_cache:
        try:
            bpy.context.scene.sn.unregister_cache[key]()
        except Exception as error:
            print(error)



class ScriptingNodesTree(bpy.types.NodeTree):

    bl_idname = 'ScriptingNodesTree'
    bl_label = "Visual Scripting"
    bl_icon = 'FILE_SCRIPT'
    is_sn = True

    link_cache = {} # stores cache of the links from the previous update for all node trees based on their memory adress

    node_refs: bpy.props.CollectionProperty(type=NodeRefCollection,
                                        name="Node References",
                                        description="A collection of groups that hold references to nodes of a specific idname")

    
    def node_collection(self, idname):
        """ Returns the collection for the given node idname refs in this node trees """
        if idname in self.node_refs:
            return self.node_refs[idname]
        return {"name": idname, "refs": []}
    

    def _map_link_to_sockets(self, link):
        """ Maps the given link to a tuple of the from socket, to socket and the link itself """
        from_real = None
        if getattr(link.to_socket, "is_sn", False):
            from_real = link.to_socket.from_socket()
        return (link.from_socket, link.to_socket, from_real, link)


    def is_valid_connection(self, from_out, to_inp):
        """ Check if a connection between the given sockets would be valid """
        if from_out and from_out.is_program == to_inp.is_program:
            # check if multiple program sockets are connected
            if to_inp.is_program:
                to_sockets = from_out.to_sockets(check_validity=False)
                if to_inp != to_sockets[0]:
                    return False
                return True
            # data types are the same
            elif from_out.bl_label == to_inp.bl_label:
                return True
            # check if data types are convertible
            else:
                if from_out.bl_label in CONVERSIONS:
                    if to_inp.bl_label in CONVERSIONS[from_out.bl_label]:
                        return True
                return False
        return False

    def is_valid_link(self, link):
        """ Checks if the given link is valid """
        # all links connected to reroutes inputs are valid
        if not getattr(link.to_socket, "is_sn", False): return True

        # get the sockets and return their validity
        to_inp = link.to_socket
        from_out = link.to_socket.from_socket()
        return self.is_valid_connection(from_out, to_inp)


    def _update_post(self):
        """ Only do visual aspects in here as this is run after evaluating the nodes """
        # TODO check time of this function to see if it impacts performance (when more complex node setups are possible)
        # mark links as invalid
        for link in self.links:
            if not self.is_valid_link(link):
                link.is_valid = False


    def _update_changed_links(self, links):
        """ Forces the affected nodes to update depending on if it's a program or data socket """
        for from_out, to_inp, _, _ in links:
            # update data sockets
            if getattr(to_inp, "is_sn", False) and not to_inp.is_program and to_inp.node:
                to_inp.force_update()
            # update program sockets
            elif getattr(from_out, "is_sn", False) and from_out.is_program and from_out.node:
                from_out.force_update()


    def _call_link_inserts(self, added):
        """ Calls link_insert for all new links """
        for _, to_inp, from_real, _ in added:
            if from_real:
                from_real.node.link_insert(from_real, to_inp, is_output=True)
                to_inp.node.link_insert(from_real, to_inp, is_output=False)

    def _call_link_removes(self, removed):
        """ Calls link_remove for all removed links """
        for _, to_inp, from_real, _ in removed:
            if from_real:
                if from_real.node:
                    from_real.node.link_remove(from_real, to_inp, is_output=True)
                if to_inp.node:
                    to_inp.node.link_remove(from_real, to_inp, is_output=False)


    def _update_added_links(self, added):
        """ Triggers an update on the given links data outputs and program inputs to update the affected program """
        self._update_changed_links(added)
        self._call_link_inserts(added)

    def _update_removed_links(self, removed):
        """ Triggers an update on the given links data inputs and program outputs to update the affected program """
        self._update_changed_links(removed)
        self._call_link_removes(removed)


    def _update_tree_links(self):
        """ Finds all changed node links and updates the connections """
        # get current links
        curr_links = list(map(self._map_link_to_sockets, self.links.values()))

        if id(self) in self.link_cache:
            # update added links
            added = list(set(curr_links) - set(self.link_cache[id(self)]))
            self._update_added_links(added)
            # update removed links
            removed = list(set(self.link_cache[id(self)]) - set(curr_links))
            self._update_removed_links(removed)

        # update cached current links
        self.link_cache[id(self)] = curr_links

        # calls a function after the links are realized
        bpy.app.timers.register(self._update_post, first_interval=0.001)


    def update(self):
        self._update_tree_links()


    def compile(self, hard=False):
        """ Compile all nodes in this node tree. If hard is true every node is also reevaluated. Use this if duplicates in other graphs could exist """
        # evaluate all nodes
        if hard:
            for node in self.nodes:
                if hasattr(node, "is_trigger"):
                    node._evaluate(bpy.context)
        # get trigger nodes
        compile_nodes = []
        for node in self.nodes:
            if getattr(node, "is_trigger", False):
                compile_nodes.append(node)
        # compile sorted nodes
        for node in sorted(compile_nodes, key=lambda node: node.order):
            node.compile()


    def graph_unregister(self):
        """ Unregister all nodes in this node tree """
        for node in self.nodes:
            if getattr(node, "is_trigger", False):
                node.node_unregister()