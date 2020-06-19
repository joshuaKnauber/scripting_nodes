import bpy
from .error_handling import ErrorHandler

class SocketHandler():

    # CALLABLE FUNCTIONS
    # socket_value: takes a socket and returns the code and errors for that socket
    # get_layout_type: returns the layout type for the given sockets connected node

    def _handle_input_socket(self, socket, socket_types):
        """ returns the connected socket as well as errors """
        value = []
        errors = []
        if socket.links[0].from_node.bl_idname != "NodeReroute":
            if socket.links[0].from_socket.bl_idname in socket_types:
                value = [socket.links[0].from_socket]
            else:
                errors.append({"error": "wrong_socket_inp", "node": socket.node})
        else:
            current_socket = socket.links[0]
            while current_socket.from_node.bl_idname == "NodeReroute":
                if len(current_socket.from_node.links) > 1:
                    current_socket = current_socket.links[0]
                else:
                    errors.append({"error": "no_connection_inp", "node": socket.node})

            if current_socket.from_socket.bl_idname in socket_types:
                value = [current_socket.from_socket]
            else:
                errors.append({"error": "wrong_socket_inp", "node": socket.node})

        return value, errors


    def _handle_output_socket(self, socket, socket_types):
        """ returns the connected socket as well as errors """
        value = []
        errors = []
        if socket.links[0].to_node.bl_idname != "NodeReroute":
            if socket.links[0].to_socket.bl_idname in socket_types:
                value = [socket.links[0].to_socket]
            else:
                errors.append({"error": "wrong_socket_out", "node": socket.node})
        else:
            current_socket = socket.links[0]
            while current_socket.to_node.bl_idname == "NodeReroute":
                if len(current_socket.to_node.links) > 1:
                    current_socket = current_socket.links[0]
                else:
                    errors.append({"error": "no_connection_out", "node": socket.node})
            value = [current_socket.to_socket]
        return value, errors


    def _handle_socket_connection(self, socket, socket_types):
        """ returns the connected socket for in and outputs, as well as errors """
        errors = []

        if socket.is_linked:
            is_input = False
            for inp in socket.node.inputs:
                if inp == socket:
                    is_input = True
            if is_input:
                value, errors = self._handle_input_socket(socket, socket_types)
            else:
                value, errors = self._handle_output_socket(socket, socket_types)
        else:
            value = []
            errors.append({"error": "no_connection", "node": socket.node})

        return value, errors


    def _get_text(self, socket):
        """ gets the code of a text socket """
        
        errors = []
        if socket.is_linked:
            value, errors = self._handle_socket_connection(socket, ["SN_StringSocket"])
        else:
            value = [socket.value]
            if '"' in value[0]:
                value = [value[0].replace('"', '\"')]
            value = ["\""] + value + ["\""]

        if not value:
            value = [""]
        return value, errors
    
    def _get_number(self, socket):
        """ gets the code of a number socket """
        
        errors = []
        if socket.is_linked:
            value, errors = self._handle_socket_connection(socket, ["SN_IntSocket", "SN_FloatSocket"])
            if socket.bl_idname == "SN_IntSocket" and value[0].bl_idname == "SN_FloatSocket":
                value = ["int(", value[0], ")"]
        else:
            value = [str(socket.value)]

        if not value:
            value = ["0"]
        return value, errors

    def _get_bool(self, socket):
        """ gets the code of a boolean socket """
        
        errors = []
        if socket.is_linked:
            value, errors = self._handle_socket_connection(socket, ["SN_BooleanSocket"])
        else:
            value = [str(socket.value)]

        if not value:
            value = ["True"]
        return value, errors

    def _get_data(self, socket):
        """ gets the code of a data socket """
        
        value, errors = self._handle_socket_connection(socket, ["SN_DataSocket", "SN_StringSocket", "SN_IntSocket", "SN_FloatSocket", "SN_BooleanSocket", "SN_VectorSocket"])

        return value, errors

    def _get_vector(self, socket):
        """ gets the code of a vector socket """

        errors = []
        if socket.is_linked:
            value, errors = self._handle_socket_connection(socket, ["SN_VectorSocket"])
        else:
            value = [str((socket.value[0], socket.value[1], socket.value[2]))]

        return value, errors

    def _get_enum(self, socket):
        """ gets the code of a enum socket """
        
        errors = []
        if socket.is_linked:
            value, errors = self._handle_socket_connection(socket, ["SN_EnumSocket"])
        else:
            value = ["\"" + socket.value + "\""]

        return value, errors

    def _get_layout(self, socket, as_list):
        """ gets the code of a layout socket """
        
        value, errors = self._handle_socket_connection(socket, ["SN_LayoutSocket"])

        if as_list or not value:
            return value, errors
        else:
            return value[0], errors

    def _get_program(self, socket, as_list):
        """ gets the code of a program socket """
        
        value, errors = self._handle_socket_connection(socket, ["SN_ProgramSocket"])

        if as_list or not value:
            return value, errors
        else:
            return value[0], errors

    def _get_scene_data(self, socket):
        """ gets the code of a scene data socket """
    
        value, errors = self._handle_socket_connection(socket, ["SN_SceneDataSocket"])

        return value, errors

    def get_layout_type(self, socket):
        """ returns the layout type for the given socket """
        layout_type = "layout"
        errors = []
        if socket.is_linked:
            if socket.links[0].to_socket.bl_idname == "SN_LayoutSocket":
                layout_type =  socket.links[0].to_node.layout_type()
            else:
                errors.append({"error": "wrong_socket_out", "node": socket.node})
        else:
            errors.append({"error": "no_connection", "node": socket.node})
        return layout_type, errors

    def socket_value(self, socket,as_list=True):
        """ returns the code and errors for that socket """
        socket_type = socket.bl_idname
        
        if socket_type == "SN_StringSocket":
            return self._get_text(socket)
        
        elif socket_type in ["SN_IntSocket", "SN_FloatSocket"]:
            return self._get_number(socket)
        
        elif socket_type == "SN_BooleanSocket":
            return self._get_bool(socket)
        
        elif socket_type == "SN_DataSocket":
            return self._get_data(socket)
        
        elif socket_type == "SN_VectorSocket":
            return self._get_vector(socket)
        
        elif socket_type == "SN_EnumSocket":
            return self._get_enum(socket)
        
        elif socket_type == "SN_LayoutSocket":
            return self._get_layout(socket, as_list)
        
        elif socket_type == "SN_ProgramSocket":
            return self._get_program(socket, as_list)
        
        elif socket_type == "SN_SceneDataSocket":
            return self._get_scene_data(socket)

