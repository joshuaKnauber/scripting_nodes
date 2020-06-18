import bpy

class ErrorMessageHandler():

    # CALLABLE FUNCTIONS
    # handle_text: takes in text and returns the updated text to use in the file

    errors = {
        "test_error": {
            "name": "Test error",
            "message": "this is the errors description",
            "fatal": True
        },
        "wrong_socket_inp": {
            "name": "Wrong socket",
            "message": "One of the inputs of this node has an incorrect output connected",
            "fatal": True
        },
        "no_connection_inp": {
            "name": "No connection",
            "message": "One of the inputs of this node has no output connected",
            "fatal": True
        },
        "wrong_socket_out": {
            "name": "Wrong socket",
            "message": "One of the outputs of this node has an incorrect input connected",
            "fatal": True
        },
        "no_connection_out": {
            "name": "No connection",
            "message": "One of the outputs of this node has no input connected",
            "fatal": True
        },
        "no_connection": {
            "name": "No connection",
            "message": "One of the sockets of this node has no connection",
            "fatal": True
        },
        "no_name_func": {
            "name": "No name function",
            "message": "The function doesn't have a name",
            "fatal": True
        },
        "no_name_panel": {
            "name": "No name panel",
            "message": "The panel doesn't have a name",
            "fatal": True
        }
    }

    def error_name(self, key):
        """ returns the error name for the given error """
        if key in self.errors:
            return self.errors[key]["name"]
        return ""

    def error_message(self, key):
        """ returns the error message for the given error """
        if key in self.errors:
            return self.errors[key]["message"]
        return ""

    def error_fatal(self, key):
        """ returns if the error is fatal for the given error """
        if key in self.errors:
            return self.errors[key]["fatal"]
        return False