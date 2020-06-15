import bpy
from .error_handling import ErrorHandler

class SocketHandler():

    # CALLABLE FUNCTIONS
    # socket_value: takes a socket and returns the code and errors for that socket

    def _handle_input_socket(self, socket, socket_types):
        """ returns the connected socket as well as errors """
        value = []
        errors = []
        if socket.links[0].from_node.bl_idname != "NodeReroute":
            if socket.links[0].from_socket.bl_idname in socket_types:
                value = [socket.links[0].from_socket]
            else:
                errors.append("wrong_socket")
        else:
            current_socket = socket.links[0]
            while current_socket.from_node.bl_idname == "NodeReroute":
                if len(current_socket.from_node.links) > 1:
                    current_socket = current_socket.links[0]
                else:
                    errors.append("no_connection")
            value = [current_socket.from_socket]
        return value, errors


    def _handle_output_socket(self, socket, socket_types):
        """ returns the connected socket as well as errors """
        value = []
        errors = []
        if socket.links[0].to_node.bl_idname != "NodeReroute":
            if socket.links[0].to_socket.bl_idname in socket_types:
                value = [socket.links[0].to_socket]
            else:
                errors.append("wrong_socket")
        else:
            current_socket = socket.links[0]
            while current_socket.to_node.bl_idname == "NodeReroute":
                if len(current_socket.to_node.links) > 1:
                    current_socket = current_socket.links[0]
                else:
                    errors.append("no_connection")
            value = [current_socket.to_socket]
        return value, errors


    def _handle_socket_connection(self, socket, socket_types):
        """ returns the connected socket for in and outputs, as well as errors """
        errors = []

        if socket.is_linked:
            if socket in socket.node.inputs:
                value, errors = self._handle_input_socket(socket, socket_types)
            else:
                value, errors = self._handle_output_socket(socket, socket_types)
        else:
            value = []
            errors.append("no_connection")

        return value, errors


    def _get_text(self, socket):
        """ gets the code of a text socket """
        
        errors = []
        if socket.is_linked:
            value, errors = self._handle_socket_connection(self, socket, ["SN_StringSocket"])
        else:
            value = [socket.value]
            if '"' in value[0]:
                value = [value[0].replace('"', '\"')]

        return value, errors
    
    def _get_number(self, socket):
        """ gets the code of a number socket """
        
        errors = []
        if socket.is_linked:
            value, errors = self._handle_socket_connection(self, socket, ["SN_IntSocket", "SN_FloatSocket"])
            if socket.bl_idname == "SN_IntSocket" and value.bl_idname == "SN_FloatSocket":
                value = ["int(", value, ")"]
        else:
            value = [socket.value]

        return value, errors

    def _get_bool(self, socket):
        """ gets the code of a boolean socket """
        
        errors = []
        if socket.is_linked:
            value, errors = self._handle_socket_connection(self, socket, ["SN_BoolSocket"])
        else:
            value = [socket.value]

        return value, errors

    def _get_data(self, socket):
        """ gets the code of a data socket """
        
        value, errors = self._handle_socket_connection(self, socket, ["SN_DataSocket", "SN_StringSocket", "SN_IntSocket", "SN_FloatSocket", "SN_BoolSocket", "SN_VectorSocket"])

        return value, errors

    def _get_vector(self, socket):
        """ gets the code of a vector socket """

        errors = []
        if socket.is_linked:
            value, errors = self._handle_socket_connection(self, socket, ["SN_VectorSocket"])
        else:
            value = [socket.value]

        return value, errors

    def _get_enum(self, socket):
        """ gets the code of a enum socket """
        
        errors = []
        if socket.is_linked:
            value, errors = self._handle_socket_connection(self, socket, ["SN_EnumSocket"])
        else:
            value = [socket.value]

        return value, errors

    def _get_layout(self, socket, as_list):
        """ gets the code of a layout socket """
        
        value, errors = self._handle_socket_connection(self, socket, ["SN_LayoutSocket"])

        if as_list or not value:
            return value, errors
        else:
            return value[0], errors

    def _get_program(self, socket, as_list):
        """ gets the code of a program socket """
        
        value, errors = self._handle_socket_connection(self, socket, ["SN_ProgramSocket"])

        if as_list or not value:
            return value, errors
        else:
            return value[0], errors

    def _get_scene_data(self, socket):
        """ gets the code of a scene data socket """
    
        value, errors = self._handle_socket_connection(self, socket, ["SN_SceneDataSocket"])

        return value, errors

    def socket_value(socket,as_list=False):
        """ returns the code and errors for that socket """
        socket_type = socket.bl_idname
        
        if socket_type == "SN_StringSocket":
            return self._get_text(socket)
        
        elif socket_type in ["SN_IntSocket", "SN_FloatSocket"]:
            return self._get_number(socket)
        
        elif socket_type == "SN_BoolSocket":
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

