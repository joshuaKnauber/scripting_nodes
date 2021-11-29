import bpy


class ScriptingNodesTree(bpy.types.NodeTree):

    bl_idname = 'ScriptingNodesTree'
    bl_label = "Visual Scripting"
    bl_icon = 'FILE_SCRIPT'
    is_sn = True

    link_cache = {} # stores cache of the links from the previous update for all node trees based on their memory adress
    

    def _map_link_to_sockets(self, link):
        """ Maps the given link to a tuple of the from socket, to socket and the link itself """
        return (link.from_socket, link.to_socket, link)


    def is_valid_connection(self, from_out, to_inp):
        """ Check if a connection between the given sockets would be valid """
        # TODO: check if data types are convertible
        if from_out and from_out.is_program == to_inp.is_program:
            # check if multiple program sockets are connected
            if to_inp.is_program:
                to_sockets = from_out.to_sockets(check_validity=False)
                if to_inp != to_sockets[0]:
                    return False
            return True
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
        # TODO check time of this function to see if it impacts performance
        # mark links as invalid
        for link in self.links:
            if not self.is_valid_link(link):
                link.is_valid = False


    def _update_changed_links(self, links):
        """ Forces the affected nodes to update depending on if it's a program or data socket """
        for from_out, to_inp, _ in links:
            # update data sockets
            if getattr(to_inp, "is_sn", False) and not to_inp.is_program:
                to_inp.force_update()
            # update program sockets
            elif getattr(from_out, "is_sn", False) and from_out.is_program:
                from_out.force_update()

    def _update_added_links(self, added):
        """ Triggers an update on the given links data outputs and program inputs to update the affected program """
        self._update_changed_links(added)
        # call insert link function here WIP
        for _, _, link in added:
            pass

    def _update_removed_links(self, removed):
        """ Triggers an update on the given links data inputs and program outputs to update the affected program """
        self._update_changed_links(removed)


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