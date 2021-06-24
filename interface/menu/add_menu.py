import bpy
from ...node_tree.node_categories import get_node_categories


from_socket = None


def sockets_compatible(socket1, socket2):
    addon_prefs = bpy.context.preferences.addons[__name__.partition('.')[
        0]].preferences

    if socket1.bl_idname == socket2.bl_idname:
        return True
    if socket1.bl_idname == socket2.to_add_idname:
        return True
    if socket1.to_add_idname == socket2.bl_idname:
        return True
    if socket1.socket_type == "DATA" and socket2.group == "DATA":
        return True

    if addon_prefs.show_all_compatible and socket1.group == "DATA" and socket2.group == "DATA":
        return True

    return False


def get_compat_socket(from_socket, node):
    if from_socket.is_output:
        for inp in node.inputs:
            if sockets_compatible(from_socket, inp):
                return inp

    else:
        for out in node.outputs:
            if sockets_compatible(from_socket, out):
                return out

    return None


class SN_OT_RunAddMenu(bpy.types.Operator):
    bl_idname = "sn.run_add_menu"
    bl_label = "Run Add Menu"
    bl_description = "Opens the add menu"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    start_x: bpy.props.FloatProperty()
    start_y: bpy.props.FloatProperty()

    def execute(self, context): return {"FINISHED"}

    def start_loc_in_bounds(self, left, bottom, right, top):
        buffer = 20
        if self.start_x >= left-buffer and self.start_x <= right+buffer:
            return self.start_y >= bottom-buffer and self.start_y <= top+buffer
        return False

    def get_from_node(self, ntree):
        for node in ntree.nodes:
            loc = node.location
            if not node.bl_idname == "NodeFrame":
                if self.start_loc_in_bounds(loc[0], loc[1]-node.dimensions[1], loc[0]+node.dimensions[0], loc[1]):
                    return node
        return None

    def from_output(self, node):
        return self.start_x > node.location[0] + node.dimensions[0]//2

    def set_socket(self, from_node):
        global from_socket
        from_socket = None

        if from_node:
            if self.from_output(from_node):
                y_offset = abs(self.start_y - from_node.location[1])
                index = int((y_offset - 30) // 20)
                if index < len(from_node.outputs) and index >= 0:
                    from_socket = from_node.outputs[index]
                    return True

            else:
                y_offset = abs(
                    self.start_y - from_node.location[1] + from_node.dimensions[1])
                index = len(from_node.inputs) - int((y_offset + 10) // 20)
                if index < len(from_node.inputs) and index >= 0:
                    from_socket = from_node.inputs[index]
                    return True

        return False

    def is_valid_node(self, context, from_node, idname):
        global from_socket

        if idname in ["NodeReroute", "NodeFrame"]:
            return False

        temp_node = context.space_data.node_tree.nodes.new(idname)
        is_valid = get_compat_socket(from_socket, temp_node) != None
        context.space_data.node_tree.nodes.remove(temp_node)
        return is_valid

    def invoke(self, context, event):
        from_node = self.get_from_node(context.space_data.node_tree)
        found_socket = self.set_socket(from_node)

        if event.shift and event.type == "LEFTMOUSE" and found_socket:

            context.scene.sn.sn_compat_nodes.clear()
            for category in get_node_categories():
                cat_item = context.scene.sn.sn_compat_nodes.add()
                cat_item.name = category.name

                for node in category.items(context):
                    if self.is_valid_node(context, from_node, node.nodetype):
                        item = cat_item.items.add()
                        item.name = "  " + node.label
                        item.identifier = node.nodetype

            bpy.ops.wm.call_menu("INVOKE_DEFAULT", name="SN_MT_AddNodeMenu")
        return {"FINISHED"}


class SN_OT_AddNode(bpy.types.Operator):
    bl_idname = "sn.add_node"
    bl_label = "Add Node"
    bl_description = "Adds this node"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    idname: bpy.props.StringProperty()

    def link_nodes(self, tree, node, from_socket):
        connect_socket = get_compat_socket(from_socket, node)

        if connect_socket:
            if from_socket.is_output:
                link = tree.links.new(from_socket, connect_socket)
            else:
                link = tree.links.new(connect_socket, from_socket)
            from_socket.node.after_link_insert(link)
            connect_socket.node.after_link_insert(link)

    def execute(self, context):
        global from_socket

        if from_socket:
            from_node = context.space_data.node_tree.nodes.active
            bpy.ops.node.add_node(type=self.idname)
            node = context.space_data.node_tree.nodes.active

            if not from_socket.is_output:
                node.location = (node.location[0]-node.width, node.location[1])

            self.link_nodes(context.space_data.node_tree, node, from_socket)
            from_socket = None
        return {"FINISHED"}


class SN_MT_AddNodeSubMenu(bpy.types.Menu):
    bl_idname = "SN_MT_AddNodeSubMenu"
    bl_label = "Add Compatible"

    def draw(self, context):
        layout = self.layout

        for item in context.category.items:
            op = layout.operator("sn.add_node", text=item.name)
            op.idname = item.identifier


class SN_MT_AddNodeMenu(bpy.types.Menu):
    bl_idname = "SN_MT_AddNodeMenu"
    bl_label = "Add Compatible"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("node.add_search", text="Search...",
                        icon="VIEWZOOM").use_transform = True

        for category in context.scene.sn.sn_compat_nodes:
            if len(category.items):
                row = layout.row()
                row.context_pointer_set("category", category)
                row.menu("SN_MT_AddNodeSubMenu", text=category.name)
